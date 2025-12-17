## Инициализация данных (Seeding)

Система использует нормализованную базу данных. Перед запуском парсера (`Ingestor`) необходимо заполнить справочники предметов и городов.

1.  Установите зависимости (если еще не установлены):
    ```bash
    pip install -r requirements.txt
    # Убедитесь, что установлен httpx
    ```

2.  Запустите скрипт наполнения:
    ```bash
    # Из корня проекта
    python -m src.scripts.seed_db
    ```

    **Ожидаемый вывод:**
    ```text
    INFO - Checking locations...
    INFO - Successfully added 8 locations.
    INFO - Checking items table...
    INFO - Downloading items from [https://raw.githubusercontent.com/](https://raw.githubusercontent.com/)...
    INFO - Parsed 8540 valid items ready for insertion.
    INFO - Inserted chunk: 5000 / 8540
    INFO - Inserted chunk: 8540 / 8540
    INFO - Items seeding completed.
    ```