import asyncio
import logging
from asyncio import Semaphore
from typing import Dict

from src.config import settings
from src.db.database import async_session_factory
from src.ingesting.repository import IngestorRepository
from src.ingesting.client import AlbionApiClient
from src.ingesting.processor import PriceProcessor

logger = logging.getLogger(__name__)


class IngestorService:
    def __init__(self, client: AlbionApiClient, processor: PriceProcessor):
        self.client = client
        self.processor = processor
        self.semaphore = Semaphore(settings.INGESTOR_CONCURRENCY)
        self.running = True
        self._location_map: Dict[str, int] = {}

    async def _init_cache(self):
        async with async_session_factory() as session:
            repo = IngestorRepository(session)
            self._location_map = await repo.get_location_map()
        logger.info(f"Loaded {len(self._location_map)} locations into cache")

    async def start(self):
        logger.info("Starting Ingestor Worker...")
        try:
            await self._init_cache()
        except Exception as e:
            logger.critical(f"Failed to initialize location cache: {e}")
            return

        try:
            while self.running:
                await self._worker_loop()
        except asyncio.CancelledError:
            logger.info("Ingestor Worker cancelled.")
        except Exception as e:
            logger.exception(f"Critical error in Ingestor Worker: {e}")
        finally:
            logger.info("Ingestor Worker stopped.")

    async def _worker_loop(self):
        async with async_session_factory() as session:
            repo = IngestorRepository(session)
            tasks_by_city = await repo.get_outdated_items(settings.INGESTOR_BATCH_SIZE)

            if not tasks_by_city:
                logger.info(f"No tasks found. Sleeping for {settings.INGESTOR_SLEEP_SEC}s")
                await asyncio.sleep(settings.INGESTOR_SLEEP_SEC)
                return

            coroutines = []
            for city_api_name, items in tasks_by_city.items():
                coroutines.append(self._process_location(city_api_name, items))

            await asyncio.gather(*coroutines)

    async def _process_location(self, city_api_name: str, items: list[str]):
        async with self.semaphore:
            location_id = self._location_map.get(city_api_name)

            if not location_id:
                logger.error(f"Location '{city_api_name}' not found in cache. Skipping batch.")
                return

            logger.info(f"Processing {city_api_name} (ID: {location_id}): {len(items)} items")

            try:
                # A: Network
                raw_dtos = await self.client.fetch_prices(items, city_api_name)

                # B: Logic (ТОЛЬКО ЦЕНЫ)
                prices_data = self.processor.process(raw_dtos)

                # C: DB Transaction
                async with async_session_factory() as session:
                    repo = IngestorRepository(session)
                    # Сохраняем только цены и обновляем last_check
                    await repo.save_batch_results(
                        prices_data,
                        items,
                        location_id
                    )

                logger.info(f"Successfully processed {city_api_name}")

            except Exception as e:
                logger.exception(f"Error processing location {city_api_name}: {e}")

            await asyncio.sleep(settings.INGESTOR_RATE_LIMIT)
            await asyncio.sleep(3.0)

    def stop(self):
        self.running = False