import re
from typing import List, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.seeding.core.interfaces import IDataProvider
from src.db.models import Item, Location


RESOURCE_TYPES = [
    "ORE", "WOOD", "HIDE", "FIBER", "ROCK",            # Ress
    "METALBAR", "PLANKS", "LEATHER", "CLOTH", "STONEBLOCK"  # Materials
]

# Regular expression for resource names
RESOURCE_PATTERN = re.compile(rf"^T[1-8]_({'|'.join(RESOURCE_TYPES)})(_LEVEL\d+@\d+)?$")


class DatabaseProvider(IDataProvider):
    def __init__(self, session: AsyncSession, resource_only: bool = False):
        """
        :param session: Database session
        :param resource_only: If True, provider will return only items
                              that are resources (by regex).
                              If False, will return ALL items from the database.
        """
        self.session = session
        self.resource_only = resource_only

    async def fetch(self) -> Dict[str, List[int]]:
        # 1. Request ID and UniqueName
        # unique_name is needed for regular expression verification
        items_stmt = select(Item.id, Item.unique_name)
        items_result = await self.session.execute(items_stmt)
        all_items = items_result.all()  # List of tuples (id, unique_name)

        #2. Filtering items
        if self.resource_only:
            # We only keep the IDs whose unique_name matches the resource template
            item_ids = [
                row.id for row in all_items
                if row.unique_name and RESOURCE_PATTERN.match(row.unique_name)
            ]
        else:
            # Old behavior: we take absolutely everything
            item_ids = [row.id for row in all_items]

        # 3. Request locations (all cities are needed here)
        locations_result = await self.session.execute(select(Location.id))
        location_ids = locations_result.scalars().all()

        return {
            "item_ids": item_ids,
            "location_ids": list(location_ids)
        }