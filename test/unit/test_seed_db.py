import asyncio
import logging
import sys
import os

# --- 1. НАСТРОЙКА ОКРУЖЕНИЯ ---
# Фейковые переменные для Pydantic, если нет .env файла
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_USER", "fake_user")
os.environ.setdefault("DB_PASS", "fake_pass")
os.environ.setdefault("DB_NAME", "fake_db")
os.environ.setdefault("MODE", "TEST")

# Добавляем корень проекта в sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
# Если скрипт лежит в корне или tests, корректируем путь.
# Предполагаем, что вы запускаете его из корня или папки скриптов.
# Лучше всего добавить текущую директорию:
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# --- 2. ИМПОРТЫ ПРОЕКТА (ОБНОВЛЕННЫЕ) ---
try:
    # ИМПОРТИРУЕМ НОВЫЕ КЛАССЫ, А НЕ СТАРЫЕ ФУНКЦИИ
    from src.config import get_settings
    from trash.data_loader import AlbionDataLoader
except ImportError as e:
    print("!!! Ошибка импорта. Проверьте, что вы находитесь в корне проекта.")
    print(f"Ошибка: {e}")
    sys.exit(1)

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(message)s")


async def debug_run():
    print(f"=== DRY RUN: ТЕСТ НОВОГО СИДЕРА (SOLID) ===")

    # Получаем настройки и инициализируем загрузчик
    settings = get_settings()
    loader = AlbionDataLoader()

    print(f"URL: {settings.SEED_ITEMS_URL}")
    print(f"Filter Tiers: {settings.SEED_MIN_TIER} - {settings.SEED_MAX_TIER}")

    # 1. Тест скачивания
    print(f"\n[1] Скачивание JSON (через AlbionDataLoader)...")
    try:
        # Теперь метод не принимает URL, он берет его из конфига внутри класса
        raw_data = await loader.fetch_items()
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
        # Вызываем метод экземпляра класса.
        # _parse_single_item формально "protected", но для тестов допустимо.
        parsed = loader._parse_single_item(raw)

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
    print("-" * 110)
    print(f"{'Unique Name':<35} | {'Base Name':<25} | {'Tier':<5} | {'Ench':<5} | {'Display Name'}")
    print("-" * 110)

    for item in valid_items[:5]:
        print(
            f"{item['unique_name']:<35} | {item['base_name']:<25} | {item['tier']:<5} | {item['enchantment_level']:<5} | {item['display_name']}")

    # 4. Проверка сложных кейсов
    print("\n[4] Проверка парсинга зачарований (Enchantment > 0):")
    print("-" * 110)
    enchanted_samples = [i for i in valid_items if i['enchantment_level'] >= 3][:3]
    if enchanted_samples:
        for item in enchanted_samples:
            print(
                f"{item['unique_name']:<35} | {item['base_name']:<25} | {item['tier']:<5} | {item['enchantment_level']:<5} | {item['display_name']}")
    else:
        print("Зачарованные предметы не найдены (возможно, отфильтрованы по тиру).")

    # 5. Итоговая сводка
    print("\n=== СВОДКА ===")
    print("Распределение по Тирам:")
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