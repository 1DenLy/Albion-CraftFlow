from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_
from sqlalchemy.dialects.postgresql import insert as pg_insert
from datetime import datetime, timezone, timedelta

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
            min_update_interval: timedelta
    ) -> Dict[str, List[str]]:
        """
        Возвращает мапу {location_api_name: [item_unique_name, ...]}.
        Выбираем TrackedItems, у которых last_check старый или None.
        """
        # Считаем "протухшим" временем: сейчас - интервал
        cutoff_time = datetime.now(timezone.utc) - min_update_interval

        stmt = (
            select(Item.unique_name, Location.api_name)
            .join(TrackedItem, TrackedItem.item_id == Item.id)
            .join(Location, TrackedItem.location_id == Location.id)
            .where(TrackedItem.is_active == True)
            .where(
                or_(
                    TrackedItem.last_check == None,
                    TrackedItem.last_check < cutoff_time
                )
            )
            .order_by(TrackedItem.last_check.asc().nulls_first())
            .limit(batch_size)
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        tasks = {}
        for item_name, loc_name in rows:
            if loc_name not in tasks:
                tasks[loc_name] = []
            tasks[loc_name].append(item_name)

        return tasks

    async def save_batch_results(
            self,
            prices_data: List[Dict[str, Any]],
            items_checked: List[str],
            location_id: int
    ) -> None:
        """
        Сохраняет цены и обновляет время проверки у предметов.
        Транзакционно.
        """

        # --- ИСПРАВЛЕНИЕ ОШИБКИ ТРАНЗАКЦИЙ ---
        # Проверяем, не открыта ли уже транзакция (неявная от SELECT).
        # Если да - коммитим её, чтобы начать чистый блок begin().
        if self.session.in_transaction():
            await self.session.commit()
        # -------------------------------------

        async with self.session.begin():
            # 1. Сначала нужно получить ID предметов
            all_names = set(items_checked)
            for p in prices_data:
                all_names.add(p['item_id'])

            # Преобразуем set в list для in_
            name_to_id_map = await self.get_item_map(list(all_names))

            # 2. Upsert Prices
            clean_prices = []
            for p in prices_data:
                i_id = name_to_id_map.get(p['item_id'])
                if i_id:
                    p_copy = p.copy()
                    p_copy['item_id'] = i_id
                    p_copy['location_id'] = location_id
                    clean_prices.append(p_copy)

            if clean_prices:
                stmt_price = pg_insert(MarketPrice).values(clean_prices)
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
            # Берем только те предметы, которые реально существуют в items
            tracked_ids_int = [name_to_id_map[name] for name in items_checked if name in name_to_id_map]

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