import asyncio
import logging
import signal
import sys
from datetime import timedelta
from aiolimiter import AsyncLimiter

# logging for worker
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("Worker")

# Imports
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

# Cycle flag
running = True


def handle_signal(signum, frame):
    """
    Signal handler for shutdown signals (SIGINT, SIGTERM).
    Switches the running flag to False, allowing the loop to finish correctly.
    """
    global running
    logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
    running = False


async def main():
    logger.info("Starting Ingestor Worker...")

    # 1. Load config
    config = IngestorConfig()

    logger.info(f"Config loaded. Max Rate: {config.max_rate}/s, Concurrency: {config.concurrency}")

    # 2. Initiating RateLimiter (Singleton)
    if config.max_rate < 1:
        limiter_rate = 1
        limiter_period = 1.0 / config.max_rate
    else:
        limiter_rate = config.max_rate
        limiter_period = 1.0

    global_limiter = AsyncLimiter(max_rate=limiter_rate, time_period=limiter_period)

    # 3. Initialize other singletons
    client = AlbionApiClient(config)
    processor = PriceProcessor()

    logger.info("Worker initialized. Entering main loop...")

    while running:
        try:
            # 4. Unit of Work: Create a new session for each iteration
            async with async_session_maker() as session:
                repo = IngestorRepository(session)

                service = IngestorService(
                    client=client,
                    repository=repo,
                    processor=processor,
                    config=config,
                    limiter=global_limiter
                )

                # 5. Retrieve tasks
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

                for location_api_name, items in tasks_map.items():
                    if not running:
                        logger.info("Shutdown signal received during task processing. Breaking loop.")
                        break

                    # logger
                    logger.info(f"Processing batch: Location='{location_api_name}', Items={len(items)}")

                    await service.start(location_api_name, items)

        except Exception as e:
            logger.exception(f"Unexpected error in main worker loop: {e}")
            # Pause before retry
            await asyncio.sleep(5)

    logger.info("Worker process finished successfully.")


if __name__ == "__main__":
    # Systen signal
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # Run async main cycle
    asyncio.run(main())