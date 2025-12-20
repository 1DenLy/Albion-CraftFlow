from typing import List, Dict, Any, Type
from src.seeding.core.base import BaseSeeder
from src.db.models import Location

class LocationsSeeder(BaseSeeder[List[Dict[str, Any]]]):
    def __init__(self, session):
        super().__init__(session, batch_size=50)

    async def _fetch_data(self) -> List[Dict[str, Any]]:
        return [
            {"api_name": "Thetford", "display_name": "Thetford"},
            {"api_name": "Fort Sterling", "display_name": "Fort Sterling"},
            {"api_name": "Lymhurst", "display_name": "Lymhurst"},
            {"api_name": "Bridgewatch", "display_name": "Bridgewatch"},
            {"api_name": "Martlock", "display_name": "Martlock"},
            {"api_name": "Caerleon", "display_name": "Caerleon"},
            {"api_name": "Black Market", "display_name": "Black Market"},
        ]

    def transform_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return raw_data

    def get_model(self) -> Type[Location]:
        return Location

    def get_conflict_statement(self, stmt):
        return stmt.on_conflict_do_nothing(index_elements=["api_name"])