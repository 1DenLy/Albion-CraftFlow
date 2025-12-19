import httpx
import logging
from typing import List
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from src.ingesting.schemas import AlbionPriceDTO
from src.ingesting.config import IngestorConfig
from src.ingesting.interfaces import IAlbionApiClient

logger = logging.getLogger(__name__)


class AlbionApiClient(IAlbionApiClient):
    def __init__(self, config: IngestorConfig):
        self.base_url = config.albion_api_url.rstrip("/")
        self.timeout = httpx.Timeout(config.request_timeout, connect=5.0)
        self.headers = {
            "User-Agent": "AlbionCraftFlowProject/1.0",
            "Accept": "application/json"
        }

    @retry(
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True
    )
    async def fetch_prices(self, items: List[str], location: str) -> List[AlbionPriceDTO]:
        """
        Запрашивает цены для списка предметов.
        Предполагается, что items уже разбит на допустимые батчи вызывающей стороной.
        """
        if not items:
            return []

        items_str = ",".join(items)
        url = f"{self.base_url}/stats/prices/{items_str}"

        # Params. В реальности API может требовать locations и qualities как query params
        params = {
            "locations": location,
            "qualities": "1,2,3,4,5"
        }

        async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
            try:
                response = await client.get(url, params=params)

                if response.status_code == 404:
                    # API может вернуть 404, если данных нет вообще
                    logger.warning(f"Albion API returned 404 for batch starting with {items[0]}")
                    return []

                if response.status_code == 429:
                    logger.warning("Rate limit hit (429) inside client.")
                    response.raise_for_status()

                response.raise_for_status()
                data = response.json()

                # Валидация через Pydantic
                return [AlbionPriceDTO.model_validate(item) for item in data]

            except httpx.HTTPStatusError as e:
                # 404 обрабатываем мягко, 429 и 5xx вызовут retry
                if e.response.status_code == 404:
                    return []
                logger.error(f"HTTP error fetching prices: {e}")
                raise e
            except Exception as e:
                logger.exception(f"Unexpected error in AlbionApiClient: {e}")
                raise