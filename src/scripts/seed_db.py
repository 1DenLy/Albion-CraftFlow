import asyncio
import logging
import re
import sys
from typing import List, Dict, Any, Optional

# Используем httpx для асинхронных запросов (pip install httpx)
import httpx
from sqlalchemy import select, func, insert
from sqlalchemy.ext.asyncio import AsyncSession

# Импортируем модели и настройки БД
# Убедитесь, что пути импорта корректны для вашей структуры проекта
from src.db.database import async_session_maker, engine, Base
from src.db.models import Item, Location

# --- Конфигурация ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
logger = logging.getLogger("seed_db")

ITEMS_JSON_URL = "https://raw.githubusercontent.com/broderickhyman/ao-bin-dumps/master/formatted/items.json"

# Список городов вынесен в константу для легкого редактирования
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


# --- Логика Локаций ---

async def seed_locations(session: AsyncSession) -> None:
    """
    Проверяет и наполняет таблицу локаций.
    Использует ORM, так как записей мало (<100).
    """
    logger.info("Checking locations...")

    # Оптимизация: проверяем наличие записей через count, чтобы не тянуть данные
    stmt = select(func.count(Location.id))
    result = await session.execute(stmt)
    count = result.scalar() or 0

    if count > 0:
        logger.info(f"Locations table already has {count} entries. Skipping.")
        return

    logger.info("Seeding locations...")
    new_locations = [
        Location(api_name=loc["api_name"], display_name=loc["display_name"])
        for loc in CORE_LOCATIONS
    ]
    session.add_all(new_locations)
    await session.commit()
    logger.info(f"Successfully added {len(new_locations)} locations.")


# --- Логика Предметов ---

async def fetch_items_data(url: str) -> List[Dict[str, Any]]:
    """
    Асинхронно скачивает JSON с предметами.
    """
    logger.info(f"Downloading items from {url}...")
    async with httpx.AsyncClient() as client:
        try:
            # Увеличиваем timeout, так как файл может быть большим
            response = await client.get(url, timeout=60.0, follow_redirects=True)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Downloaded {len(data)} items.")
            return data
        except httpx.RequestError as e:
            logger.error(f"Network error while downloading items: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return []


def parse_item_dict(raw_item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Чистая функция (Pure Function).
    Преобразует сырой JSON-объект в словарь, пригодный для вставки в SQL.
    Возвращает None, если предмет нужно пропустить.
    """
    unique_name = raw_item.get("UniqueName")
    if not unique_name:
        return None

    # Фильтр мусорных предметов
    if "TEST" in unique_name or "TUTORIAL" in unique_name:
        return None

    localized = raw_item.get("LocalizedNames", {})
    display_name = localized.get("EN-US") if localized else unique_name

    # Разбор имени: T4_MAIN_SWORD@1
    # По умолчанию
    tier = 1
    enchantment = 0
    base_name = unique_name

    # 1. Попытка распарсить Tier и убрать префикс
    # Ищем паттерн T + цифра + подчеркивание в начале
    tier_match = re.match(r"^T(\d+)_", unique_name)
    if tier_match:
        tier = int(tier_match.group(1))
        # Отрезаем "T4_" от начала строки для base_name
        base_name = unique_name[len(tier_match.group(0)):]

    # 2. Попытка распарсить Enchantment (@X)
    if "@" in base_name:
        parts = base_name.split("@")
        base_name = parts[0]
        # Проверяем, является ли вторая часть числом
        if len(parts) > 1 and parts[1].isdigit():
            enchantment = int(parts[1])

    return {
        "unique_name": unique_name,
        "base_name": base_name,
        "tier": tier,
        "enchantment_level": enchantment,
        "display_name": display_name
    }


async def bulk_insert_items(session: AsyncSession, items_data: List[Dict[str, Any]]) -> int:
    """
    Использует SQLAlchemy Core Insert для максимальной скорости.
    Вставляет данные пачками.
    """
    if not items_data:
        return 0

    # Размер пачки (Chunk size)
    CHUNK_SIZE = 5000
    total_inserted = 0

    # Итерация по списку с шагом CHUNK_SIZE
    for i in range(0, len(items_data), CHUNK_SIZE):
        chunk = items_data[i: i + CHUNK_SIZE]
        # Core statement: insert(Model).values([...])
        stmt = insert(Item).values(chunk)

        # Если используем PostgreSQL и хотим игнорировать дубликаты (опционально):
        # from sqlalchemy.dialects.postgresql import insert as pg_insert
        # stmt = pg_insert(Item).values(chunk).on_conflict_do_nothing()

        await session.execute(stmt)
        await session.commit()
        total_inserted += len(chunk)
        logger.info(f"Inserted chunk: {total_inserted} / {len(items_data)}")

    return total_inserted


async def seed_items(session: AsyncSession) -> None:
    """Оркестратор наполнения предметов."""
    logger.info("Checking items table...")

    # Быстрая проверка количества
    count = (await session.execute(select(func.count(Item.id)))).scalar() or 0

    # Если база уже наполнена (например, > 1000 записей), пропускаем
    if count > 1000:
        logger.info(f"Items table already contains {count} records. Skipping seed.")
        return

    # 1. Скачиваем
    raw_data = await fetch_items_data(ITEMS_JSON_URL)
    if not raw_data:
        logger.warning("No data downloaded. Aborting.")
        return

    # 2. Парсим (CPU-bound операция, но для 5-10к предметов Python справится быстро)
    # Используем генератор списков для фильтрации None
    parsed_items = []
    for raw in raw_data:
        parsed = parse_item_dict(raw)
        if parsed:
            parsed_items.append(parsed)

    logger.info(f"Parsed {len(parsed_items)} valid items ready for insertion.")

    # 3. Вставляем (I/O bound)
    await bulk_insert_items(session, parsed_items)
    logger.info("Items seeding completed.")


# --- Точка входа ---

async def main():
    try:
        # Создаем таблицы (в продакшене лучше использовать Alembic миграции)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with async_session_maker() as session:
            await seed_locations(session)
            await seed_items(session)

    except Exception as e:
        logger.critical(f"Critical error during seeding: {e}", exc_info=True)
    finally:
        # Корректно закрываем соединение с движком
        await engine.dispose()


if __name__ == "__main__":
    # Фикс для Windows (ProactorEventLoop)
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())