# Ingestor Module: Архітектура та Процеси

## 1. Загальне призначення

Модуль **ingestor** відповідає за фонову актуалізацію ринкових даних. Він працює як автономний демон (worker), який:

- сканує базу даних на наявність застарілих записів;
- запитує свіжі дані у зовнішнього API (Albion Online Data Project);
- зберігає результати, формуючи історичні тренди.

---

## 2. Архітектурний стиль

Модуль побудований за принципами **Clean Architecture** та **SOLID**, з явним акцентом на:

- **Dependency Inversion Principle (DIP)**
- **Separation of Concerns (SoC)**

### Ключові компоненти (діаграма класів)

- **Worker** (`worker.py`)
  - Composition Root
  - Точка входу
  - Збір усіх залежностей (DI)
  - Запуск нескінченного циклу обробки
  - Graceful Shutdown (обробка сигналів ОС)

- **Service** (`service.py` → `IngestorService`)
  - Оркестратор бізнес-логіки
  - Керує потоком даних, конкурентністю та лімітами
  - Не знає деталей HTTP або SQL

- **Client** (`client.py` → `AlbionApiClient`)
  - Інфраструктурний шар (Network)
  - Реалізує `IAlbionApiClient`
  - HTTP-запити, заголовки, retries

- **Processor** (`processor.py` → `PriceProcessor`)
  - Чиста бізнес-логіка (Pure Functions)
  - Перетворення DTO → структури БД
  - Фільтрація сміттєвих даних

- **Repository** (`repository.py` → `IngestorRepository`)
  - Інфраструктурний шар (Persistence)
  - Реалізує `IIngestorRepository`
  - SQL, Upsert, транзакції

---

## 3. Детальний процес роботи (Data Flow)

Повний цикл оновлення складається з 5 етапів.

### Етап 1: Планування (Scheduling)

**Де:** `worker.py` → `repository.get_outdated_items`

- Воркер опитує таблицю `tracked_items`
- Умови вибірки:
  - `last_check` старіший за `min_update_interval` (за замовчуванням 30 хв)
  - або `last_check IS NULL`
- Пріоритезація:
  - `priority DESC`
  - `last_check ASC`
- Групування:
  - по локаціях (наприклад, Martlock)

---

### Етап 2: Оркестрація та контроль навантаження

**Де:** `service.py` → `start()`

- Отримання списку предметів для локації (наприклад, 1000 ID)

**Batching**:
- Розбиття на чанки по `batch_size` (за замовчуванням 50)
- Захист від `414 URI Too Long`

**Concurrency**:
- `asyncio.Semaphore`
- Наприклад, `concurrency = 5`

**Rate Limiting**:
- Token Bucket (`aiolimiter`)
- Захист від `HTTP 429`

---

### Етап 3: Отримання даних (Extract)

**Де:** `client.py` → `fetch_prices`

- **Resilience** (`tenacity`):
  - 5xx → Exponential Backoff (1s, 2s, 4s…)
  - 429 → повтор запиту
  - 404 → повертається `[]`

- **Validation**:
  - Pydantic-схема `AlbionPriceDTO`
  - Відсікання невалідних даних

---

### Етап 4: Трансформація (Transform)

**Де:** `processor.py` → `process`

- Фільтрація нульових цін (sell = 0 та buy = 0)
- Mapping міст → `location_id`
- Enrichment:
  - часові мітки

---

### Етап 5: Збереження (Load)

**Де:** `repository.py` → `save_batch_results`

Одна транзакція PostgreSQL:

- **Upsert (Snapshot)**:
  - Таблиця `market_prices`
  - `ON CONFLICT (item_id, location_id, quality_level) DO UPDATE`

- **Insert (History)**:
  - Таблиця `market_history`
  - Append-only лог

- **Acknowledge**:
  - Оновлення `tracked_items.last_check = NOW()`

> ⚠️ `last_check` оновлюється для всього батчу, навіть якщо API не повернув дані

**Навіщо:**
- Захист від "петлі смерті"
- Повторна перевірка лише через 30 хв

---

## 4. Прийняті технічні рішення (ADR)

### Рішення 1: Protocol замість абстрактних класів

**Де:** `interfaces.py`

**Чому:**
- Структурна типізація (Duck Typing)
- Простіші моки та юніт-тести
- Краще відповідає DIP

---

### Рішення 2: Явне управління конкурентністю

**Де:** `service.py`, `config.py`

- `Semaphore` — контроль ресурсів БД
- `AsyncLimiter` — контроль RPS до API

Дозволяє незалежно керувати паралельністю та швидкістю

---

### Рішення 3: Валідація на кордоні системи

**Де:** `schemas.py`, `client.py`

**Чому:**
- Недовіра до зовнішніх даних
- Помилки виявляються рано
- Зрозумілі exception замість SQL-помилок

---

### Рішення 4: Snapshot vs History

**Де:** `repository.py`

- `market_prices` — швидкі запити для UI
- `market_history` — часові ряди для аналітики

> Спрощений CQRS на рівні схеми БД

---

### Рішення 5: Управління життєвим циклом через Worker

**Чому:**
- Відокремлення від FastAPI (`main.py`)
- Незалежне масштабування
- Graceful shutdown через `signal`

---

## 5. Потенційні точки розширення

- **Proxy Rotation**
  - Реалізація у `client.py`
  - Інтерфейс не змінюється

- **Redis Cache**
  - Винесення `location_map` з памʼяті
  - Актуально при горизонтальному масштабуванні

- **Message Broker**
  - RabbitMQ / Kafka замість polling
  - Події типу: `UpdateItemPrice`

