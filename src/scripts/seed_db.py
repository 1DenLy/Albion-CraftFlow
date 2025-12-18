import asyncio
import logging
import sys
from pathlib import Path

import logging

# --- ВСТАВЛЯЕМ СЮДА ---
# Отключаем вывод SQL-запросов (оставляем только WARNING и ERROR)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
# ---------------------

# Добавляем корневую директорию проекта в sys.path, чтобы Python видел пакет src
# Это позволяет запускать скрипт как файл: python src/scripts/seed_db.py
sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.db.database import async_session_maker
from src.config import get_settings
from src.seeding.manager import SeedingManager



# Настройка простого логирования для скрипта
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    settings = get_settings()

    logger.info("Initializing database session...")

    async with async_session_maker() as session:
        try:
            manager = SeedingManager(session, settings)
            await manager.seed()
        except Exception as e:
            logger.error(f"Seeding failed: {e}")
            sys.exit(1)


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())