import itertools
from typing import List, Dict, Any, Type
from src.seeding.core.base import BaseSeeder
from src.seeding.core.interfaces import IDataProvider
from src.db.models import TrackedItem


class TrackedItemsSeeder(BaseSeeder[Dict[str, List[int]]]):
    def __init__(self, session, provider: IDataProvider):
        super().__init__(session, batch_size=5000)
        self.provider = provider

    async def _fetch_data(self) -> Dict[str, List[int]]:
        return await self.provider.fetch()

    def transform_data(self, raw_data: Dict[str, List[int]]) -> List[Dict[str, Any]]:
        item_ids = raw_data.get("item_ids", [])
        location_ids = raw_data.get("location_ids", [])

        if not item_ids or not location_ids:
            return []

        pairs = itertools.product(item_ids, location_ids)

        return [
            {
                "item_id": item_id,
                "location_id": loc_id,
                "is_active": True,
                "priority": 1
            }
            for item_id, loc_id in pairs
        ]

    def get_model(self) -> Type[TrackedItem]:
        return TrackedItem

    def get_conflict_statement(self, stmt):
        # ON CONFLICT DO NOTHING
        return stmt.on_conflict_do_nothing(
            index_elements=["item_id", "location_id"]
        )