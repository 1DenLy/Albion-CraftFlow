import asyncio
import json
import logging
import re
import sys
import requests
from typing import List, Dict, Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

# Импортируем твои модели и настройки
# Обрати внимание: скрипт должен запускаться из корня проекта как модуль
from src.db.database import async_session_factory, engine, Base
from src.db.models import Item, Location

# Настройка логгера
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# URL официального дампа предметов
ITEMS_JSON_URL = "https://raw.githubusercontent.com/ao-bin-dumps/formatted/master/items.json"

# Основные города Альбиона (API Names)
# Важно: display_name делаем читаемым
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


async def seed_locations(session: AsyncSession):
    """Наполняет таблицу locations, если она пуста."""
    logger.info("Checking locations...")

    # Проверяем, есть ли уже записи
    result = await session.execute(select(func.count(Location.id)))
    count = result.scalar()

    if count > 0:
        logger.info(f"Locations table already has {count} entries. Skipping.")
        return

    logger.info("Seeding locations...")
    new_locations = [Location(api_name=loc["api_name"], display_name=loc["display_name"]) for loc in CORE_LOCATIONS]
    session.add_all(new_locations)
    await session.commit()
    logger.info(f"Added {len(new_locations)} locations.")


def parse_item_data(item_data: Dict[str, Any]) -> Dict[str, Any] | None:
    """
    Преобразует JSON объект из дампа в словарь для модели Item.
    Возвращает None, если предмет нужно пропустить.
    """
    unique_name = item_data.get("UniqueName")
    if not unique_name:
        return None

    # Фильтр: пропускаем системные предметы, заглушки и прочий мусор
    # Обычно предметы имеют формат T{tier}_{NAME} или просто NAME
    if "TEST" in unique_name or "TUTORIAL" in unique_name:
        return None

    # Попытка извлечь имя на английском
    localized_names = item_data.get("LocalizedNames", {})
    display_name = localized_names.get("EN-US") if localized_names else unique_name

    # --- Логика разбора имени ---
    # Пример: T4_MAIN_SWORD@1
    # Tier: 4
    # Base: MAIN_SWORD
    # Enchant: 1

    tier = 1
    enchantment = 0
    base_name = unique_name

    # 1. Извлекаем Tier (T4_...)
    tier_match = re.match(r"^T(\d+)_", unique_name)
    if tier_match:
        tier = int(tier_match.group(1))
        # Убираем префикс T4_ для base_name
        base_name = unique_name[len(tier_match.group(0)):]

    # 2. Извлекаем Enchantment (@1)
    if "@" in base_name:
        parts = base_name.split("@")
        base_name = parts[0]
        try:
            enchantment = int(parts[1])
        except (IndexError, ValueError):
            enchantment = 0

    # Если enchantment не нашли в имени, пробуем из JSON (иногда там есть поле)
    # Но в UniqueName оно надежнее.

    return {
        "unique_name": unique_name,
        "base_name": base_name,
        "tier": tier,
        "enchantment_level": enchantment,
        "display_name": display_name
    }


async def seed_items(session: AsyncSession):
    """Скачивает и наполняет таблицу items."""
    logger.info("Checking items...")

    # Если база уже наполнена, не тратим время (там >5000 предметов)
    result = await session.execute(select(func.count(Item.id)))
    count = result.scalar()
    if count > 1000:
        logger.info(f"Items table already has {count} entries. Skipping download.")
        return

    logger.info(f"Downloading items.json from {ITEMS_JSON_URL} ...")
    try:
        response = requests.get(ITEMS_JSON_URL, stream=True, timeout=30)
        response.raise_for_status()
        items_list = response.json()
    except Exception as e:
        logger.error(f"Failed to download items: {e}")
        return

    logger.info(f"Downloaded {len(items_list)} raw items. Parsing...")

    batch = []
    batch_size = 1000
    total_added = 0

    for raw_item in items_list:
        parsed = parse_item_data(raw_item)
        if parsed:
            # Создаем объект модели
            item = Item(
                unique_name=parsed["unique_name"],
                base_name=parsed["base_name"],
                tier=parsed["tier"],
                enchantment_level=parsed["enchantment_level"],
                display_name=parsed["display_name"]
            )
            batch.append(item)

        # Bulk Insert пачками
        if len(batch) >= batch_size:
            session.add_all(batch)
            await session.commit()
            total_added += len(batch)
            batch = []
            logger.info(f"Processed {total_added} items...")

    # Добавляем остаток
    if batch:
        session.add_all(batch)
        await session.commit()
        total_added += len(batch)

    logger.info(f"Successfully seeded {total_added} items.")


async def main():
    """Точка входа"""
    # Создаем таблицы, если их нет (на всякий случай)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        await seed_locations(session)
        await seed_items(session)


if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())