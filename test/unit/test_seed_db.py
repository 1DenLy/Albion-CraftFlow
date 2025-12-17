import asyncio
import logging
import sys
import os

# --- 1. НАСТРОЙКА ОКРУЖЕНИЯ (ОЧЕНЬ ВАЖНО: ДО ИМПОРТОВ ИЗ SRC) ---

# Устанавливаем фейковые переменные окружения, чтобы Pydantic Settings не падал.
# Это нужно, потому что при запуске через `python ...` файл conftest.py игнорируется.
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_USER", "fake_user")
os.environ.setdefault("DB_PASS", "fake_pass")
os.environ.setdefault("DB_NAME", "fake_db")
os.environ.setdefault("MODE", "TEST")

# Добавляем корень проекта в sys.path, чтобы Python видел папку 'src'
# (Поднимаемся на 2 уровня вверх от папки unit: unit -> test -> Albion-CraftFlow)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- 2. ИМПОРТЫ ПРОЕКТА (ТЕПЕРЬ БЕЗОПАСНО) ---
try:
    from src.scripts.seed_db import fetch_items_data, parse_item_dict, ITEMS_JSON_URL
except ImportError as e:
    print("!!! Ошибка импорта. Проверьте структуру проекта.")
    print(f"Путь к корню определен как: {project_root}")
    print(f"Ошибка: {e}")
    sys.exit(1)

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(message)s")


async def debug_run():
    print(f"=== DRY RUN: ТЕСТ СИДЕРА ===")
    print(f"URL: {ITEMS_JSON_URL}")

    # 1. Тест скачивания
    print(f"\n[1] Скачивание JSON...")
    try:
        raw_data = await fetch_items_data(ITEMS_JSON_URL)
    except Exception as e:
        print(f"!!! CRITICAL: Не удалось скачать файл: {e}")
        return

    if not raw_data:
        print("!!! ПУСТО: Пришел пустой список данных.")
        return

    print(f"--> OK. Скачано объектов: {len(raw_data)}")

    # 2. Тест парсинга
    print("\n[2] Парсинг и валидация...")
    valid_items = []
    skipped_count = 0

    # Статистика
    tiers_found = {}
    enchants_found = {}

    for raw in raw_data:
        parsed = parse_item_dict(raw)
        if parsed:
            valid_items.append(parsed)

            # Сбор статистики
            t = parsed['tier']
            e = parsed['enchantment_level']

            tiers_found[t] = tiers_found.get(t, 0) + 1
            if e > 0:
                enchants_found[e] = enchants_found.get(e, 0) + 1
        else:
            skipped_count += 1

    print(f"--> Готово к вставке (Valid): {len(valid_items)}")
    print(f"--> Отброшено (Skipped): {skipped_count}")

    # 3. Примеры данных
    print("\n[3] Случайные примеры (Первые 5):")
    print("-" * 100)
    print(f"{'Unique Name':<35} | {'Base Name':<25} | {'Tier':<5} | {'Ench':<5} | {'Display Name'}")
    print("-" * 100)

    for item in valid_items[:5]:
        print(
            f"{item['unique_name']:<35} | {item['base_name']:<25} | {item['tier']:<5} | {item['enchantment_level']:<5} | {item['display_name']}")

    # 4. Проверка сложных кейсов (Зачарования)
    print("\n[4] Проверка парсинга зачарований (Enchantment > 0):")
    print("-" * 100)
    enchanted_samples = [i for i in valid_items if i['enchantment_level'] >= 3][:3]
    if enchanted_samples:
        for item in enchanted_samples:
            print(
                f"{item['unique_name']:<35} | {item['base_name']:<25} | {item['tier']:<5} | {item['enchantment_level']:<5} | {item['display_name']}")
    else:
        print("Зачарованные предметы не найдены.")

    # 5. Итоговая сводка
    print("\n=== СВОДКА ===")
    print("Распределение по Тирам:")
    # Выводим только первые 10 для краткости, если их много
    sorted_tiers = sorted(tiers_found.keys())
    for t in sorted_tiers:
        print(f"  Tier {t}: {tiers_found[t]} шт.")

    print("\nНайдено зачарований:")
    for e in sorted(enchants_found.keys()):
        print(f"  Level {e}: {enchants_found[e]} шт.")


if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(debug_run())