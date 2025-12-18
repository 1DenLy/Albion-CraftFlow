import asyncio
import json
import logging
import sys
import os
from typing import List

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

# Импорты из вашего проекта
# Обратите внимание: путь к src должен быть в PYTHONPATH
sys.path.append(os.getcwd())

from src.db.database import async_session_maker, engine
from src.db.models import Item, Location, TrackedItem

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
logger = logging.getLogger("seed_tracking")

RESOURCES_FILE = "resources.json"


async def seed_tracking_data():
    if not os.path.exists(RESOURCES_FILE):
        logger.error(f"File {RESOURCES_FILE} not found. Run generate_resources_json.py first.")
        return

    # 1. Читаем список уникальных имен ресурсов
    with open(RESOURCES_FILE, "r", encoding="utf-8") as f:
        target_unique_names: List[str] = json.load(f)

    logger.info(f"Loaded {len(target_unique_names)} items from JSON.")

    async with async_session_maker() as session:
        # 2. Получаем ID всех локаций (городов)
        # Мы хотим отслеживать ресурсы во всех городах из таблицы locations
        loc_stmt = select(Location.id)
        locations_result = await session.execute(loc_stmt)
        location_ids = locations_result.scalars().all()

        if not location_ids:
            logger.error("No locations found in DB. Run seed_db.py first!")
            return

        # 3. Получаем ID предметов, соответствующих нашим ресурсам
        # Делаем это одним запросом или чанками, если список очень большой.
        # Для ~1000 ресурсов можно одним запросом.
        item_stmt = select(Item.id, Item.unique_name).where(Item.unique_name.in_(target_unique_names))
        items_result = await session.execute(item_stmt)
        items_map = items_result.all()  # Список кортежей (id, unique_name)

        found_item_ids = [row[0] for row in items_map]

        logger.info(f"Found {len(found_item_ids)} matching items in DB (out of {len(target_unique_names)} requested).")

        if not found_item_ids:
            logger.warning("No matching items found via SQL lookup. Ensure seed_db.py populated items.")
            return

        # 4. Подготавливаем данные для вставки (Cross Join: Items * Locations)
        tracking_entries = []
        for item_id in found_item_ids:
            for loc_id in location_ids:
                tracking_entries.append({
                    "item_id": item_id,
                    "location_id": loc_id,
                    "is_active": True,
                    "priority": 1  # Базовый приоритет
                })

        logger.info(f"Prepared {len(tracking_entries)} tracking entries (Items * Locations).")

        # 5. Bulk Insert с игнорированием дубликатов
        # Разбиваем на чанки по 5000 записей, чтобы не забить память/драйвер
        CHUNK_SIZE = 5000
        total_inserted = 0

        for i in range(0, len(tracking_entries), CHUNK_SIZE):
            chunk = tracking_entries[i: i + CHUNK_SIZE]

            stmt = insert(TrackedItem).values(chunk)
            # Если запись уже есть, ничего не делаем (idempotency)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=['item_id', 'location_id']  # Constraint PK
            )

            await session.execute(stmt)
            await session.commit()
            total_inserted += len(chunk)
            logger.info(f"Processed chunk {i}..{i + len(chunk)}")

        logger.info("Tracking seeding completed successfully.")


async def main():
    try:
        await seed_tracking_data()
    except Exception as e:
        logger.critical(f"Error seeding tracking: {e}", exc_info=True)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())