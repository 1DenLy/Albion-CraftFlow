import re
from typing import List, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.seeding.core.interfaces import IDataProvider
from src.db.models import Item, Location

# --- Конфигурация фильтров (перенесено из trash/generate_resources_json.py) ---
RESOURCE_TYPES = [
    "ORE", "WOOD", "HIDE", "FIBER", "ROCK",            # Сырые ресурсы
    "METALBAR", "PLANKS", "LEATHER", "CLOTH", "STONEBLOCK"  # Переработанные
]

# Регулярка: T[1-8]_ + TYPE + опционально LEVEL (зачарование)
# Пример совпадения: T4_WOOD, T8_CLOTH_LEVEL3@3
RESOURCE_PATTERN = re.compile(rf"^T[1-8]_({'|'.join(RESOURCE_TYPES)})(_LEVEL\d+@\d+)?$")


class DatabaseProvider(IDataProvider):
    def __init__(self, session: AsyncSession, resource_only: bool = False):
        """
        :param session: Сессия базы данных
        :param resource_only: Если True, провайдер вернет только предметы,
                              являющиеся ресурсами (по regex).
                              Если False, вернет ВСЕ предметы из базы.
        """
        self.session = session
        self.resource_only = resource_only

    async def fetch(self) -> Dict[str, List[int]]:
        # 1. Запрашиваем ID и UniqueName
        # unique_name нужен для проверки регулярным выражением
        items_stmt = select(Item.id, Item.unique_name)
        items_result = await self.session.execute(items_stmt)
        all_items = items_result.all()  # Список кортежей (id, unique_name)

        # 2. Фильтрация предметов
        if self.resource_only:
            # Оставляем только те ID, чьи unique_name подходят под шаблон ресурсов
            item_ids = [
                row.id for row in all_items
                if row.unique_name and RESOURCE_PATTERN.match(row.unique_name)
            ]
        else:
            # Старое поведение: берем абсолютно всё
            item_ids = [row.id for row in all_items]

        # 3. Запрашиваем локации (тут нужны все города)
        locations_result = await self.session.execute(select(Location.id))
        location_ids = locations_result.scalars().all()

        return {
            "item_ids": item_ids,
            "location_ids": list(location_ids)
        }