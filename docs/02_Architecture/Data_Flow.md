# Data Flow (Поток данных)

## Архитектурная особенность: Mapping
Внешний API (Albion Data Project) оперирует строками (`T4_MAIN_SWORD`, `Lymhurst`).
Наша БД оперирует числами (`item_id=504`, `location_id=4`).

**Ingestor Service** выступает переводчиком. Он должен держать в памяти (или кэшировать) соответствие `String <-> Int`.

## Детальный цикл Ingestor Service

### Шаг 1: Selection (Выборка задач)
1.  `Ingestor` обращается к таблице `tracked_items`.
2.  **Query:** Выбрать записи, где `is_active=True`, отсортировать по `last_check ASC`.
3.  **Join:** Подтянуть `items.unique_name` и `locations.api_name`, так как они нужны для составления URL.
4.  **Batching:** Сгруппировать 50-100 предметов для одного города.

### Шаг 2: Extraction (Запрос к API)
1.  Сформировать URL:
    `GET /api/v2/stats/prices/T4_BAG,T4_CAPE?locations=Lymhurst`
2.  Получить JSON ответ (`MarketResponse` array).

### Шаг 3: Resolution & Transformation (Обработка)
Для каждого объекта из JSON ответа:
1.  **Resolve IDs:**
    * Взять `itemTypeId` (строка) -> Найти наш локальный `item_id` (int).
    * Взять `city` (строка) -> Найти наш локальный `location_id` (int).
    * *Примечание:* Если ID не найден (например, новый предмет), запись пропускается или логируется warning.
2.  **Mapping:** Преобразовать поля JSON в поля модели SQLAlchemy:
    * `sellPriceMin` -> `sell_price_min`
    * `qualityLevel` -> `quality_level`

### Шаг 4: Loading (Сохранение)
Выполняется транзакция:
1.  **Upsert MarketPrice:**
    ```sql
    INSERT INTO market_prices (...) VALUES (...)
    ON CONFLICT (item_id, location_id, quality_level)
    DO UPDATE SET sell_price_min = EXCLUDED.sell_price_min, ...
    ```
2.  **Update TrackedItem:**
    Обновить `last_check = NOW()` для обработанных пар (item_id, location_id).

## Диаграмма JSON Mapping

Mapping `api_structhure.json` -> `models.py`:

| JSON Field (API) | DB Column (Model) | Тип данных | Примечание |
| :--- | :--- | :--- | :--- |
| `itemTypeId` | `item_id` | String -> Int | Требует Lookup по таблице items |
| `city` | `location_id` | String -> Int | Требует Lookup по таблице locations |
| `qualityLevel` | `quality_level` | Int | 1=Normal, 2=Good... |
| `sellPriceMin` | `sell_price_min` | Int | Цена Sell Order |
| `sellPriceMinDate` | `sell_price_min_date` | DateTime | Время обновления |
| `buyPriceMax` | `buy_price_max` | Int | Цена Buy Order |