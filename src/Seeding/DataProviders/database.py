from typing import List, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.seeding.core.interfaces import IDataProvider
from src.db.models import Item, Location


class DatabaseProvider(IDataProvider):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def fetch(self) -> Dict[str, List[int]]:
        # Fetch item IDs
        items_result = await self.session.execute(select(Item.id))
        item_ids = items_result.scalars().all()

        # Fetch location IDs
        locations_result = await self.session.execute(select(Location.id))
        location_ids = locations_result.scalars().all()

        return {
            "item_ids": list(item_ids),
            "location_ids": list(location_ids)
        }