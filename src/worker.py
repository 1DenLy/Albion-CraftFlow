import asyncio
import logging
import signal
import sys
from datetime import timedelta
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

    # 1. Загружаем конфиг ПЕРВЫМ делом
    config = IngestorConfig()

    logger.info(f"Config loaded. Max Rate: {config.max_rate}/s, Concurrency: {config.concurrency}")

    # 2. Инициализация RateLimiter (Singleton)
    if config.max_rate < 1:
        # Например: 0.6 req/s -> 1 запрос каждые ~1.66 сек
        limiter_rate = 1
        limiter_period = 1.0 / config.max_rate
    else:
        # Например: 5 req/s -> 5 запросов каждые 1.0 сек
        limiter_rate = config.max_rate
        limiter_period = 1.0

    global_limiter = AsyncLimiter(max_rate=limiter_rate, time_period=limiter_period)

    # 3. Инициализация остальных синглтонов
    client = AlbionApiClient(config)
    processor = PriceProcessor()

    logger.info("Worker initialized. Entering main loop...")

    while running:
        try:
            # 4. Unit of Work: Создаем новую сессию на каждую итерацию цикла
            async with async_session_maker() as session:
                repo = IngestorRepository(session)

                service = IngestorService(
                    client=client,
                    repository=repo,
                    processor=processor,
                    config=config,
                    limiter=global_limiter
                )

                # 5. Получение задач (SELECT)
                # Это действие открывает неявную транзакцию
                tasks_map = await repo.get_outdated_items(
                    batch_size=50,
                    min_update_interval=timedelta(minutes=30)
                )

                if not tasks_map:
                    logger.info("All tracked items are fresh (< 30 min). Sleeping 60s...")
                    for _ in range(60):
                        if not running: break
                        await asyncio.sleep(1)
                    continue

                # 6. Выполнение задач
                for location_api_name, items in tasks_map.items():
                    if not running:
                        logger.info("Shutdown signal received during task processing. Breaking loop.")
                        break

                    # Логируем начало работы над пачкой
                    logger.info(f"Processing batch: Location='{location_api_name}', Items={len(items)}")

                    # Делегируем выполнение сервису (внутри будет новая транзакция на запись)
                    await service.start(location_api_name, items)

        except Exception as e:
            logger.exception(f"Unexpected error in main worker loop: {e}")
            # Пауза перед ретраем при ошибке (например, отвал БД)
            await asyncio.sleep(5)

    logger.info("Worker process finished successfully.")


if __name__ == "__main__":
    # Регистрация сигналов ОС
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # Запуск асинхронного цикла
    asyncio.run(main())