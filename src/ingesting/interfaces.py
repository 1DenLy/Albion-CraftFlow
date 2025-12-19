from typing import Protocol, List, Dict, Any
from src.ingesting.schemas import AlbionPriceDTO


class IAlbionApiClient(Protocol):
    async def fetch_prices(self, items: List[str], location: str) -> List[AlbionPriceDTO]:
        ...


class IIngestorRepository(Protocol):
    async def get_location_map(self) -> Dict[str, int]:
        ...

    async def save_batch_results(self, prices_data: List[Dict[str, Any]], items_checked: List[str],
                                 location_id: int) -> None:
        ...