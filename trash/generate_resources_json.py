import asyncio
import json
import httpx
import re

# URL источника
ITEMS_JSON_URL = "https://raw.githubusercontent.com/ao-bin-dumps/formatted/master/items.json"
OUTPUT_FILE = "resources.json"

# Категории для поиска (упрощенная фильтрация по системным именам)
# В Albion системные имена ресурсов выглядят как T4_WOOD, T4_PLANKS_LEVEL1@1 и т.д.
RESOURCE_TYPES = [
    "ORE", "WOOD", "HIDE", "FIBER", "ROCK",  # Сырые ресурсы
    "METALBAR", "PLANKS", "LEATHER", "CLOTH", "STONEBLOCK"  # Переработанные материалы
]


async def fetch_and_filter():
    print(f"Downloading items from {ITEMS_JSON_URL}...")
    async with httpx.AsyncClient() as client:
        # Увеличиваем таймаут, так как файл большой
        response = await client.get(ITEMS_JSON_URL, timeout=60.0)
        response.raise_for_status()
        data = response.json()

    print(f"Total items fetched: {len(data)}")

    filtered_items = []

    # Регулярка для фильтрации: T[1-8]_ + (TYPE) + опционально зачарование
    # Пример: T4_WOOD, T4_PLANKS_LEVEL1@1
    pattern = re.compile(rf"^T[1-8]_({'|'.join(RESOURCE_TYPES)})(_LEVEL\d+@\d+)?$")

    for item in data:
        unique_name = item.get("UniqueName")
        if unique_name and pattern.match(unique_name):
            # Сохраняем только уникальное имя, так как остальные данные есть в items
            filtered_items.append(unique_name)

    # Удаляем дубликаты и сортируем
    filtered_items = sorted(list(set(filtered_items)))

    print(f"Filtered {len(filtered_items)} resource/material items.")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(filtered_items, f, indent=2)

    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(fetch_and_filter())