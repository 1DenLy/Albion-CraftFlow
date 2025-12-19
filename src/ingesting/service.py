import asyncio
import logging
from aiolimiter import AsyncLimiter
from typing import List

from src.ingesting.config import IngestorConfig
from src.ingesting.processor import PriceProcessor
from src.ingesting.interfaces import IAlbionApiClient, IIngestorRepository

logger = logging.getLogger(__name__)


class IngestorService:
    def __init__(
            self,
            client: IAlbionApiClient,
            repository: IIngestorRepository,  # В тестах сюда придет Mock, в проде - репозиторий с сессией
            processor: PriceProcessor,
            config: IngestorConfig
    ):
        self.client = client
        self.repository = repository
        self.processor = processor
        self.config = config

        # Rate Limiter: max_rate запросов в 1 секунду
        # Token Bucket алгоритм внутри
        self.limiter = AsyncLimiter(max_rate=config.max_rate, time_period=1.0)

        self._location_map = {}
        self.running = True

    async def _init_cache(self):
        """Загрузка кэша локаций."""
        self._location_map = await self.repository.get_location_map()
        logger.info(f"Loaded {len(self._location_map)} locations into cache")

    async def start(self, location_api_name: str, items: List[str]):
        """
        Основная точка входа для запуска воркера (упрощена для примера).
        Принимает город и список предметов для обработки.
        """
        await self._init_cache()
        await self._process_location(location_api_name, items)

    async def _process_location(self, city_api_name: str, items: List[str]):
        location_id = self._location_map.get(city_api_name)
        if not location_id:
            logger.error(f"Location '{city_api_name}' not found. Skipping.")
            return

        # SC-04: Batching Strategy. Разбиваем список предметов на чанки.
        batches = [
            items[i: i + self.config.batch_size]
            for i in range(0, len(items), self.config.batch_size)
        ]

        logger.info(f"Processing {city_api_name}: {len(items)} items in {len(batches)} batches.")

        # Ограничиваем параллелизм задач, но RateLimit контролируется отдельным лимитером
        # Если нужно строго последовательно - убираем gather и делаем for await.
        # Для соблюдения RateLimit при gather, limiter.acquire() должен быть внутри корутины.

        tasks = []
        for batch in batches:
            tasks.append(self._process_batch(batch, city_api_name, location_id))

        # Запускаем пачками по concurrency (настройка параллелизма)
        # Это предотвращает создание 1000 тасок в event loop сразу
        concurrency_sem = asyncio.Semaphore(self.config.concurrency)

        async def sem_task(task):
            async with concurrency_sem:
                return await task

        await asyncio.gather(*(sem_task(t) for t in tasks))

    async def _process_batch(self, batch_items: List[str], city_api_name: str, location_id: int):
        # SC-03: Rate Limiting. Ждем разрешения перед отправкой запроса.
        async with self.limiter:
            try:
                # A: Network
                raw_dtos = await self.client.fetch_prices(batch_items, city_api_name)

                # B: Logic
                prices_data = self.processor.process(raw_dtos)

                # C: DB (Repository вызов)
                if prices_data or raw_dtos == []:
                    # Даже если пусто, надо обновить дату проверки items (в реализации репо)
                    await self.repository.save_batch_results(
                        prices_data,
                        batch_items,
                        location_id
                    )
            except Exception as e:
                logger.exception(f"Error processing batch for {city_api_name}: {e}")