from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_  # <--- Добавлен or_
from sqlalchemy.dialects.postgresql import insert as pg_insert
from datetime import datetime, timezone, timedelta  # <--- Добавлена timedelta

# Импортируем только нужные модели.
from src.db.models import TrackedItem, Location, MarketPrice, Item


class IngestorRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_location_map(self) -> Dict[str, int]:
        """Кэш локаций: api_name -> id"""
        stmt = select(Location.api_name, Location.id)
        result = await self.session.execute(stmt)
        return {row.api_name: row.id for row in result.all()}

    async def get_item_map(self, unique_names: List[str]) -> Dict[str, int]:
        """Получает ID предметов по их уникальным именам (T4_BAG -> 55)."""
        stmt = select(Item.unique_name, Item.id).where(Item.unique_name.in_(unique_names))
        result = await self.session.execute(stmt)
        return {row.unique_name: row.id for row in result.all()}

    async def get_outdated_items(
        self,
        batch_size: int,
        min_update_interval: timedelta  # <--- Новый аргумент
    ) -> Dict[str, List[str]]:
        """
        Возвращает предметы, которые не обновлялись дольше, чем min_update_interval.
        """
        # Вычисляем время, раньше которого данные считаются "протухшими"
        # Используем UTC, так как в БД храним timezone-aware datetime
        threshold_time = datetime.now(timezone.utc) - min_update_interval

        stmt = (
            select(Item.unique_name, Location.api_name)
            .join(TrackedItem, TrackedItem.item_id == Item.id)
            .join(Location, TrackedItem.location_id == Location.id)
            .where(
                and_(
                    TrackedItem.is_active == True,
                    # Условие: Либо last_check пуст (никогда не проверяли),
                    # Либо last_check меньше (старее), чем пороговое время
                    or_(
                        TrackedItem.last_check == None,
                        TrackedItem.last_check < threshold_time
                    )
                )
            )
            # Сортируем: сначала NULL (самые приоритетные), потом самые старые
            .order_by(TrackedItem.last_check.asc().nulls_first())
            .limit(batch_size)
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        grouped_items: Dict[str, List[str]] = {}
        for unique_name, loc_api_name in rows:
            if loc_api_name not in grouped_items:
                grouped_items[loc_api_name] = []
            grouped_items[loc_api_name].append(unique_name)

        return grouped_items

    async def save_batch_results(
            self,
            prices: List[Dict[str, Any]],
            item_unique_names: List[str],
            location_id: int
    ):
        """
        Сохраняет только MarketPrice и обновляет TrackedItem.
        """
        async with self.session.begin():
            # 1. Резолвим Item IDs (строки в int)
            incoming_names = [p['item_id'] for p in prices]
            all_names_to_resolve = list(set(incoming_names + item_unique_names))

            name_to_id_map = await self.get_item_map(all_names_to_resolve)

            # Фильтруем и маппим цены (подставляем int ID)
            valid_prices = []
            for p in prices:
                if p['item_id'] in name_to_id_map:
                    p['item_id'] = name_to_id_map[p['item_id']]
                    p['location_id'] = location_id
                    valid_prices.append(p)

            # 2. Upsert Market Prices
            if valid_prices:
                stmt_price = pg_insert(MarketPrice).values(valid_prices)

                # Обновляем все поля при конфликте
                stmt_price = stmt_price.on_conflict_do_update(
                    index_elements=['item_id', 'location_id', 'quality_level'],
                    set_={
                        'sell_price_min': stmt_price.excluded.sell_price_min,
                        'sell_price_min_date': stmt_price.excluded.sell_price_min_date,
                        'sell_price_max': stmt_price.excluded.sell_price_max,
                        'sell_price_max_date': stmt_price.excluded.sell_price_max_date,

                        'buy_price_min': stmt_price.excluded.buy_price_min,
                        'buy_price_min_date': stmt_price.excluded.buy_price_min_date,
                        'buy_price_max': stmt_price.excluded.buy_price_max,
                        'buy_price_max_date': stmt_price.excluded.buy_price_max_date,

                        'last_updated': stmt_price.excluded.last_updated
                    }
                )
                await self.session.execute(stmt_price)

            # 3. Обновляем Tracked Items (время проверки)
            tracked_ids_int = [name_to_id_map[name] for name in item_unique_names if name in name_to_id_map]

            if tracked_ids_int:
                update_stmt = (
                    update(TrackedItem)
                    .where(
                        and_(
                            TrackedItem.item_id.in_(tracked_ids_int),
                            TrackedItem.location_id == location_id
                        )
                    )
                    .values(last_check=datetime.now(timezone.utc))
                )
                await self.session.execute(update_stmt)