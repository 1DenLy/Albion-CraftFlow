import re
from typing import List, Dict, Any, Type
from src.seeding.core.base import BaseSeeder
from src.seeding.config import SeedingConfig
from src.seeding.core.interfaces import IDataProvider
from src.db.models import Item


class ItemsSeeder(BaseSeeder[List[Dict[str, Any]]]):
    def __init__(self, session, config: SeedingConfig, provider: IDataProvider):
        super().__init__(session, config.batch_size)
        self.config = config
        self.provider = provider

    async def _fetch_data(self) -> List[Dict[str, Any]]:
        return await self.provider.fetch()

    def transform_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        transformed = []
        for entry in raw_data:
            unique_name = entry.get("UniqueName")
            if not unique_name:
                continue

            # Парсинг Tier и Enchantment
            # Формат: T4_BAG, T4_BAG@1
            match = re.match(r"^T(\d+)_", unique_name)
            if not match:
                continue

            tier = int(match.group(1))

            # Фильтрация по Tier
            if not (self.config.seed_min_tier <= tier <= self.config.seed_max_tier):
                continue

            parts = unique_name.split('@')
            base_name = parts[0]
            enchantment = int(parts[1]) if len(parts) > 1 else 0

            # Локализация
            localized = entry.get("LocalizedNames", {})
            display_name = localized.get("EN-US") or unique_name

            transformed.append({
                "unique_name": unique_name,
                "base_name": base_name,
                "tier": tier,
                "enchantment_level": enchantment,
                "effective_tier": tier + enchantment,
                # Computed, но можно передать явно, если нужно (обычно БД сама считает)
                "display_name": display_name
            })

        return transformed

    def get_model(self) -> Type[Item]:
        return Item

    def get_conflict_statement(self, stmt):
        # ON CONFLICT (unique_name) DO UPDATE
        return stmt.on_conflict_do_update(
            index_elements=["unique_name"],
            set_={
                "base_name": stmt.excluded.base_name,
                "tier": stmt.excluded.tier,
                "enchantment_level": stmt.excluded.enchantment_level,
                "display_name": stmt.excluded.display_name
            }
        )