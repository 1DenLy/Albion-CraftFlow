import asyncio
import logging
from aiolimiter import AsyncLimiter
from typing import List, Optional

from src.ingesting.config import IngestorConfig
from src.ingesting.processor import PriceProcessor
from src.ingesting.interfaces import IAlbionApiClient, IIngestorRepository

logger = logging.getLogger(__name__)


class IngestorService:
    def __init__(
            self,
            client: IAlbionApiClient,
            repository: IIngestorRepository,
            processor: PriceProcessor,
            config: IngestorConfig,
            limiter: Optional[AsyncLimiter] = None
    ):
        self.client = client
        self.repository = repository
        self.processor = processor
        self.config = config

        # Rate Limiter:
        if limiter:
            self.limiter = limiter
        else:
            self.limiter = AsyncLimiter(max_rate=config.max_rate, time_period=1.0)

        self._location_map = {}
        self.running = True

    async def _init_cache(self):
        """Load location cache"""
        self._location_map = await self.repository.get_location_map()
        # Логируем только если кэш пуст или при старте, чтобы не спамить в цикле воркера
        if not self._location_map:
             logger.warning("Location cache is empty!")

    async def start(self, location_api_name: str, items: List[str]):
        """
        Entry point for processing a single location
        """
        await self._init_cache()
        await self._process_location(location_api_name, items)

    async def _process_location(self, city_api_name: str, items: List[str]):
        location_id = self._location_map.get(city_api_name)
        if not location_id:
            logger.error(f"Location '{city_api_name}' not found in cache. Skipping.")
            return

        batches = [
            items[i: i + self.config.batch_size]
            for i in range(0, len(items), self.config.batch_size)
        ]

        logger.info(f"Processing {city_api_name}: {len(items)} items in {len(batches)} batches.")

        tasks = []
        for batch in batches:
            tasks.append(self._process_batch(batch, city_api_name, location_id))

        concurrency_sem = asyncio.Semaphore(self.config.concurrency)

        async def sem_task(task):
            async with concurrency_sem:
                return await task

        # RateLimit controled self.limiter in _process_batch
        await asyncio.gather(*(sem_task(t) for t in tasks))

    async def _process_batch(self, batch_items: List[str], city_api_name: str, location_id: int):
        # SC-03: Rate Limiting. Wait for token from global bucket.
        async with self.limiter:
            try:
                # A: Network
                raw_dtos = await self.client.fetch_prices(batch_items, city_api_name)

                # B: Logic
                prices_data = self.processor.process(raw_dtos)

                # C: DB
                # Save or update check time
                await self.repository.save_batch_results(
                    prices_data,
                    batch_items,
                    location_id
                )
            except Exception as e:
                logger.exception(f"Error processing batch for {city_api_name}: {e}")