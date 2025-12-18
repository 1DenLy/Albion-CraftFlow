import logging
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.seeding.config import SeedingConfig
from src.seeding.providers.albion_api import AlbionApiProvider
from src.seeding.providers.database import DatabaseProvider
from src.seeding.seeders.items import ItemsSeeder
from src.seeding.seeders.tracking import TrackedItemsSeeder


class SeedingManager:
    def __init__(self, session: AsyncSession, settings: Settings):
        self.session = session
        self.settings = settings
        self.logger = logging.getLogger(__name__)

        # Инициализация конфигурации сидинга из основных настроек
        self.config = SeedingConfig(
            items_source_url=settings.SEED_ITEMS_URL,
            seed_min_tier=settings.SEED_MIN_TIER,
            seed_max_tier=settings.SEED_MAX_TIER
        )

    async def seed(self):
        """
        Запускает процесс наполнения базы данных.
        Последовательность:
        1. Items (из внешнего API)
        2. TrackedItems (связка Items x Locations)
        """
        self.logger.info("Starting seeding process...")

        try:
            # 1. Seed Items
            await self._seed_items()

            # 2. Seed Tracked Items
            if self.config.enable_tracking_seeding:
                await self._seed_tracked_items()

            self.logger.info("Seeding completed successfully.")

        except Exception as e:
            self.logger.error("Seeding process aborted due to error.")
            raise e

    async def _seed_items(self):
        self.logger.info("Initializing ItemsSeeder...")
        provider = AlbionApiProvider(str(self.config.items_source_url))
        seeder = ItemsSeeder(self.session, self.config, provider)
        await seeder.run()

    async def _seed_tracked_items(self):
        self.logger.info("Initializing TrackedItemsSeeder...")
        provider = DatabaseProvider(self.session)
        seeder = TrackedItemsSeeder(self.session, provider)
        await seeder.run()