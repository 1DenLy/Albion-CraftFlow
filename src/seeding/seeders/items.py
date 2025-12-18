import re
from typing import List, Dict, Any, Type
from src.seeding.core.base import BaseSeeder
from src.seeding.config import SeedingConfig
from src.seeding.core.interfaces import IDataProvider
from src.db.models import Item
from src.models.items import ItemDTO

class ItemsSeeder(BaseSeeder[List[Dict[str, Any]]]):
    def __init__(self, session, config: SeedingConfig, provider: IDataProvider):
        super().__init__(session, config.batch_size)
        self.config = config
        self.provider = provider

    async def _fetch_data(self) -> List[Dict[str, Any]]:
        return await self.provider.fetch()

    def transform_data(self, raw_data: list[dict]) -> list[dict]:
        cleaned_items = []

        for entry in raw_data:
            try:
                # 1. Валидация через Pydantic
                item_model = ItemDTO.model_validate(entry)

                # --- ЛОГИКА ОПРЕДЕЛЕНИЯ ИМЕНИ ---
                # Если base_name нет (оно None из DTO), берем display_name, иначе unique_name
                final_base_name = item_model.base_name
                if not final_base_name:
                    final_base_name = item_model.display_name or item_model.unique_name

                # 2. Формируем словарь. ВАЖНО: поле 'tier' обязательно для БД!
                clean_item = {
                    "unique_name": item_model.unique_name,
                    "display_name": item_model.display_name,
                    "base_name": final_base_name,
                    "tier": item_model.tier,  # <--- Теперь это свойство есть в DTO
                    "enchantment_level": item_model.enchantment_level, # <--- И это тоже
                }

                cleaned_items.append(clean_item)

            except (AttributeError, ValueError) as e:
                self.logger.warning(f"Skipping invalid item {entry.get('UniqueName', 'UNKNOWN')}: {e}")
                continue

        return cleaned_items

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