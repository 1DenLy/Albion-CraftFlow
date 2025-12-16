# Database Schema

## Обзор
База данных спроектирована по принципам нормализации. Мы не храним строковые идентификаторы (например, "T4_BAG") в таблицах с данными, вместо этого используются целочисленные внешние ключи (`Integer FK`), ссылающиеся на справочники.

Стек: **PostgreSQL 16+** + **SQLAlchemy (Async)**.

## Таблицы-Справочники (Dictionaries)

### 1. `locations` (Города)
Справочник игровых локаций.
* **id** (`SmallInteger`, PK): Внутренний ID (1, 2, 3...).
* **api_name** (`String(50)`, Unique): Идентификатор из API (например, `Martlock`, `Black Market`).
* **display_name** (`String(100)`): Читаемое название для UI.

### 2. `items` (Предметы)
Справочник всех существующих предметов.
* **id** (`Integer`, PK): Внутренний ID.
* **unique_name** (`String(100)`, Unique): Техническое имя из API (например, `T4_BAG`).
* **base_name** (`String(50)`): Базовое имя (для группировки, например `BAG`).
* **tier** (`SmallInteger`): Тир предмета (4, 5, 6...).
* **enchantment_level** (`SmallInteger`): Зачарование (0, 1, 2, 3, 4).
* **effective_tier** (`Computed`): Вычисляемое поле (`tier + enchantment_level`). Полезно для фильтрации "мощности".
* **display_name** (`String`): Локализованное имя.

**Индексы:**
* `idx_items_high_tier`: Оптимизированный индекс для выборки предметов высокого уровня (tier >= 4).

## Таблицы Данных (Core Data)

### 3. `tracked_items` (Очередь парсинга)
Join-таблица, определяющая конфигурацию: "Какой предмет в каком городе мониторить".
* **item_id** (`FK -> items.id`, PK): Ссылка на предмет.
* **location_id** (`FK -> locations.id`, PK): Ссылка на город.
* **priority** (`SmallInteger`): Приоритет обновления (чем выше число, тем важнее).
* **is_active** (`Boolean`): Включен/выключен мониторинг.
* **last_check** (`DateTime`): Время последнего запроса к API по этой паре.

### 4. `market_prices` (Текущие цены - Snapshot)
Хранит только *последнее* известное состояние рынка для уникальной комбинации.
* **item_id** (`FK`, PK) + **location_id** (`FK`, PK) + **quality_level** (`SmallInteger`, PK): Составной первичный ключ.
* **sell_price_min** / **buy_price_max** (`BigInteger`): Цены в серебре.
* **sell_price_min_date** / **buy_price_max_date**: Время актуальности цены (из API).
* **last_updated**: Время записи строки в нашу БД.

### 5. `market_history` (Исторические данные)
Журнал для построения графиков.
* **item_id** (`FK`, PK) + **location_id** (`FK`, PK) + **quality_level** (`SmallInteger`, PK) + **timestamp** (`DateTime`, PK): Составной ключ, включающий время.
* **average_price** (`BigInteger`): Средняя цена.
* **item_count** (`BigInteger`): Количество проданных лотов (объем).

**Индексы:**
* `idx_history_item_time`: Для быстрого построения графиков "Цена предмета за период".