import asyncio
import logging
import sys

# Настраиваем логирование для скрипта
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
logger = logging.getLogger("seed_db_script")


from src.db.database import async_session_maker, engine
from trash.data_loader import AlbionDataLoader
from trash.seeder import DatabaseSeeder


async def main():
    try:
        async with async_session_maker() as session:
            # Инициализация сервисов
            data_loader = AlbionDataLoader()
            seeder = DatabaseSeeder(session)

            # Локации
            await seeder.seed_locations()

            # Предметы
            raw_data = await data_loader.fetch_items()
            parsed_items = data_loader.parse_and_filter_items(raw_data)

            # в БД
            await seeder.seed_items(parsed_items)

    except Exception as e:
        logger.critical(f"Critical error during seeding: {e}", exc_info=True)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())