import httpx
import logging
from typing import List, Any
from src.seeding.core.interfaces import IDataProvider

class AlbionApiProvider(IDataProvider):
    def __init__(self, url: str):
        self.url = url
        self.logger = logging.getLogger(__name__)

    async def fetch(self) -> List[Any]:
        async with httpx.AsyncClient() as client:
            for attempt in range(3):
                try:
                    response = await client.get(self.url)
                    response.raise_for_status()
                    return response.json()
                except httpx.HTTPStatusError as e:
                    if 500 <= e.response.status_code < 600:
                        self.logger.warning(f"Server error {e.response.status_code}, retrying ({attempt+1}/3)...")
                        if attempt == 2:
                            raise
                        continue
                    raise
                except httpx.RequestError as e:
                    self.logger.warning(f"Request error {e}, retrying ({attempt+1}/3)...")
                    if attempt == 2:
                        raise
                    continue
        return []