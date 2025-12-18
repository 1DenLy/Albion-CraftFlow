import logging
import re
from typing import List, Dict, Any, Optional
import httpx
from src.config import get_settings

# Получаем настройки один раз
settings = get_settings()
logger = logging.getLogger(__name__)


class AlbionDataLoader:
    """
    Сервис для загрузки и первичной обработки данных из внешних источников.
    Отвечает за сетевые взаимодействия и парсинг JSON.
    """

    def __init__(self):
        # Настраиваем клиент с таймаутом
        self.client = httpx.AsyncClient(timeout=60.0)

    async def fetch_items(self) -> List[Dict[str, Any]]:
        """Асинхронно скачивает сырые данные."""
        url = settings.SEED_ITEMS_URL
        logger.info(f"Downloading items from {url}...")

        try:
            response = await self.client.get(url, follow_redirects=True)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Downloaded {len(data)} items.")
            return data
        except httpx.RequestError as e:
            logger.error(f"Network error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return []
        finally:
            await self.client.aclose()

    def parse_and_filter_items(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Фильтрует и парсит список предметов.
        Pure function logic (почти), зависит только от конфига.
        """
        parsed_items = []
        for item in raw_data:
            parsed = self._parse_single_item(item)
            if parsed:
                parsed_items.append(parsed)
        return parsed_items

    def _parse_single_item(self, raw_item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        unique_name = raw_item.get("UniqueName")
        if not unique_name:
            return None

        # Базовая фильтрация мусора
        if "TEST" in unique_name or "TUTORIAL" in unique_name:
            return None

        # Логика парсинга тира
        tier = 1
        base_name = unique_name
        tier_match = re.match(r"^T(\d+)_", unique_name)
        if tier_match:
            tier = int(tier_match.group(1))
            base_name = unique_name[len(tier_match.group(0)):]

        # --- ИСПОЛЬЗОВАНИЕ КОНФИГА ---
        if not (settings.SEED_MIN_TIER <= tier <= settings.SEED_MAX_TIER):
            return None

        # Логика зачарования
        enchantment = 0
        if "@" in base_name:
            parts = base_name.split("@")
            base_name = parts[0]
            if len(parts) > 1 and parts[1].isdigit():
                enchantment = int(parts[1])

        localized = raw_item.get("LocalizedNames", {})
        display_name = localized.get("EN-US") if localized else unique_name

        return {
            "unique_name": unique_name,
            "base_name": base_name,
            "tier": tier,
            "enchantment_level": enchantment,
            "display_name": display_name
        }