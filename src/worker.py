import asyncio
import logging
import signal
import sys
from datetime import timedelta  # <--- Добавлен импорт
from aiolimiter import AsyncLimiter

# Настройка логирования для воркера
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("Worker")

# Импорты проекта
try:
    from src.ingesting.config import IngestorConfig
    from src.ingesting.client import AlbionApiClient
    from src.ingesting.repository import IngestorRepository
    from src.ingesting.processor import PriceProcessor
    from src.ingesting.service import IngestorService
    from src.db.database import async_session_maker
except ImportError as e:
    logger.critical(f"Import Error: {e}. Make sure you run this with 'python -m src.worker'")
    sys.exit(1)

# Флаг управления циклом
running = True


def handle_signal(signum, frame):
    """
    Обработчик сигналов остановки (SIGINT, SIGTERM).
    Переключает флаг running в False, позволяя циклу завершиться корректно.
    """
    global running
    logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
    running = False


async def main():
    logger.info("Starting Ingestor Worker...")

    # 1. Загрузка конфигурации (Singleton)
    config = IngestorConfig()

    # Рекомендуется установить max_rate=0.85 в env для запаса по лимитам
    logger.info(f"Config loaded. Max Rate: {config.max_rate}/s, Concurrency: {config.concurrency}")

    # 2. Инициализация долгоживущих объектов (Singleton)
    # RateLimiter создается ОДИН раз, чтобы лимиты не сбрасывались
    global_limiter = AsyncLimiter(max_rate=config.max_rate, time_period=1.0)

    client = AlbionApiClient()
    processor = PriceProcessor()

    logger.info("Worker initialized. Entering main loop...")

    while running:
        try:
            # 3. Unit of Work: Создаем новую сессию на каждую итерацию цикла
            async with async_session_maker() as session:
                repo = IngestorRepository(session)

                service = IngestorService(
                    client=client,
                    repository=repo,
                    processor=processor,
                    config=config,
                    limiter=global_limiter
                )

                # 4. Получение задач
                # Запрашиваем предметы, которые не обновлялись более 30 минут
                tasks_map = await repo.get_outdated_items(
                    batch_size=50,
                    min_update_interval=timedelta(minutes=30)  # <--- Задержка 30 мин
                )

                if not tasks_map:
                    logger.info("All tracked items are fresh (< 30 min). Sleeping 60s...")
                    # Если задач нет, спим и ждем пока предметы "постареют"
                    for _ in range(60):
                        if not running: break
                        await asyncio.sleep(1)
                    continue

                # 5. Выполнение задач
                for location_api_name, items in tasks_map.items():
                    if not running:
                        logger.info("Shutdown signal received during task processing. Breaking loop.")
                        break

                    # Логируем начало работы над пачкой
                    logger.info(f"Processing batch: Location='{location_api_name}', Items={len(items)}")

                    # Делегируем выполнение сервису
                    await service.start(location_api_name, items)

        except Exception as e:
            logger.exception(f"Unexpected error in main worker loop: {e}")
            # Пауза перед ретраем, чтобы не спамить в логи при отвале БД
            await asyncio.sleep(5)

    logger.info("Worker process finished successfully.")


if __name__ == "__main__":
    # Регистрация сигналов ОС
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # Запуск асинхронного цикла
    asyncio.run(main())