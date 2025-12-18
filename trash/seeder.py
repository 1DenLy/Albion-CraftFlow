import logging
from typing import List, Dict, Any
from sqlalchemy import select, func, insert
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import Item, Location

logger = logging.getLogger(__name__)

# Константу городов оставляем здесь или тоже выносим в конфиг/отдельный JSON,
# но пока для простоты оставим здесь, так как это static data.
CORE_LOCATIONS = [
    {"api_name": "Martlock", "display_name": "Martlock"},
    {"api_name": "Bridgewatch", "display_name": "Bridgewatch"},
    {"api_name": "Lymhurst", "display_name": "Lymhurst"},
    {"api_name": "Fort Sterling", "display_name": "Fort Sterling"},
    {"api_name": "Thetford", "display_name": "Thetford"},
    {"api_name": "Caerleon", "display_name": "Caerleon"},
    {"api_name": "Black Market", "display_name": "Black Market"},
    {"api_name": "Brecilien", "display_name": "Brecilien"},
]


class DatabaseSeeder:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def seed_locations(self) -> None:
        """Проверяет и заполняет таблицу локаций."""
        stmt = select(func.count(Location.id))
        count = (await self.session.execute(stmt)).scalar() or 0

        if count > 0:
            logger.info(f"Locations table already has {count} entries. Skipping.")
            return

        logger.info("Seeding locations...")
        # Используем bulk insert через ORM или Core
        # Core быстрее, но ORM привычнее. Здесь Core insert для скорости не критичен (мало записей),
        # но для единообразия с items используем Core style.
        await self.session.execute(insert(Location).values(CORE_LOCATIONS))
        await self.session.commit()
        logger.info("Locations seeded.")

    async def seed_items(self, items_data: List[Dict[str, Any]]) -> None:
        """
        Принимает готовые данные и вставляет их в БД пачками.
        """
        if not items_data:
            logger.warning("No items to insert.")
            return

        stmt = select(func.count(Item.id))
        count = (await self.session.execute(stmt)).scalar() or 0

        # Простая проверка: если данных много, считаем, что сидинг был
        if count > 1000:
            logger.info(f"Items table already has {count} entries. Skipping.")
            return

        logger.info(f"Starting bulk insert of {len(items_data)} items...")

        CHUNK_SIZE = 5000
        total_inserted = 0

        for i in range(0, len(items_data), CHUNK_SIZE):
            chunk = items_data[i: i + CHUNK_SIZE]
            await self.session.execute(insert(Item).values(chunk))
            await self.session.commit()
            total_inserted += len(chunk)
            logger.info(f"Inserted chunk: {total_inserted} / {len(items_data)}")

        logger.info("Items seeding completed.")