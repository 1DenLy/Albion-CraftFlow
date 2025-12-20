import logging
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.seeding.config import SeedingConfig
from src.seeding.providers.albion_api import AlbionApiProvider
from src.seeding.providers.database import DatabaseProvider
from src.seeding.seeders.items import ItemsSeeder
from src.seeding.seeders.tracking import TrackedItemsSeeder
from src.seeding.seeders.locations import LocationsSeeder


class SeedingManager:
    def __init__(self, session: AsyncSession, settings: Settings):
        self.session = session
        self.settings = settings
        self.logger = logging.getLogger(__name__)

        # Initializing the seating configuration from the basic settings
        self.config = SeedingConfig(
            items_source_url=settings.SEED_ITEMS_URL,
            seed_min_tier=settings.SEED_MIN_TIER,
            seed_max_tier=settings.SEED_MAX_TIER
        )

    async def seed(self):
        self.logger.info("Starting seeding process...")

        try:
            # 1. Seed Items
            await self._seed_items()

            # 2. Seed Locations
            await self._seed_locations()

            # 3. Seed Tracked Items
            if self.config.enable_tracking_seeding:
                await self._seed_tracked_items()

            self.logger.info("seeding completed successfully.")

        except Exception as e:
            self.logger.error("seeding process aborted due to error.")
            raise e

    async def _seed_items(self):
        self.logger.info("Initializing ItemsSeeder...")
        provider = AlbionApiProvider(str(self.config.items_source_url))
        seeder = ItemsSeeder(self.session, self.config, provider)
        await seeder.run()

    async def _seed_locations(self):
        self.logger.info("Initializing LocationsSeeder...")
        seeder = LocationsSeeder(self.session)
        await seeder.run()

    async def _seed_tracked_items(self):
        self.logger.info("Initializing TrackedItemsSeeder...")
        provider = DatabaseProvider(self.session, resource_only=True)
        seeder = TrackedItemsSeeder(self.session, provider)
        await seeder.run()