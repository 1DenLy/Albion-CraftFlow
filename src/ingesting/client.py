import httpx
from typing import List
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
import logging
from src.config import settings
from src.ingesting.schemas import AlbionPriceDTO

logger = logging.getLogger(__name__)


class AlbionApiClient:
    def __init__(self, base_url: str = settings.ALBION_API_URL):
        self.base_url = base_url.rstrip("/")
        self.timeout = httpx.Timeout(10.0, connect=5.0)

        self.headers = {
            "User-Agent": "AlbionCraftFlowProject",
            "Accept": "application/json"
        }


    @retry(
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def fetch_prices(self, items: List[str], location: str) -> List[AlbionPriceDTO]:
        """
        Запрашивает цены для списка предметов в конкретной локации.
        """
        if not items:
            return []

        # Предотвращение ошибки 414 URI Too Long, если батч слишком велик
        if len(items) > 100:
            logger.warning(f"Fetching {len(items)} items at once. Consider reducing INGESTOR_BATCH_SIZE.")

        items_str = ",".join(items)
        url = f"{self.base_url}/{items_str}"

        # qualities=1,2,3,4,5 покрывает все уровни качества
        params = {
            "locations": location,
            "qualities": "1,2,3,4,5"
        }

        async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
            try:
                response = await client.get(url, params=params)

                # Если 404 — значит данных по этим предметам сейчас нет, возвращаем пустой список,
                # чтобы сервис просто обновил дату проверки.
                if response.status_code == 404:
                    logger.warning(f"Albion API returned 404 for items batch starting with: {items[0]}")
                    return []

                # 429 Too Many Requests (если tenacity не поймает раньше)
                if response.status_code == 429:
                    logger.warning("Rate limit hit (429).")
                    response.raise_for_status()

                response.raise_for_status()
                data = response.json()

                return [AlbionPriceDTO.model_validate(item) for item in data]

            except httpx.HTTPStatusError as e:
                # 404 обработан выше, остальные пробрасываем для retry
                if e.response.status_code != 404:
                    logger.error(f"HTTP error fetching prices: {e}")
                    raise e
                return []
            except Exception as e:
                # Логируем с traceback для непредвиденных ошибок
                logger.exception(f"Unexpected error fetching prices: {e}")
                raise e