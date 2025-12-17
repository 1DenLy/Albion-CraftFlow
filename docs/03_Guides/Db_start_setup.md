# Запуск и инициализация окружения

Данный документ описывает полный процесс запуска инфраструктуры, применения миграций и сидинга данных для проекта **Albion Craftflow** с использованием Docker.

---

## 1. Запуск контейнеров

Вся инфраструктура (PostgreSQL, Adminer, API, Worker) запускается одной командой. Флаг `--build` гарантирует пересборку Docker-образов при изменении `Dockerfile`.

### Команда

```bash
docker-compose up -d --build
```

### Ожидаемый результат

```text
[+] Running 5/5
 ✔ Network albion-craftflow_default Created
 ✔ Container albion_db              Started
 ✔ Container albion_adminer         Started
 ✔ Container albion_api             Started
 ✔ Container albion_worker          Started
```

### Проверка статуса контейнеров

```bash
docker-compose ps
```

Убедитесь, что у всех контейнеров статус **Up** или **running**.

---

## 2. Применение миграций (Alembic)

После запуска контейнеров база данных создаётся пустой. Для инициализации схемы данных необходимо применить миграции Alembic. Команда выполняется **внутри контейнера API**.

### Команда

```bash
docker exec -it albion_api alembic upgrade head
```

### Ожидаемый результат

```text
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade -> ...
```

### Проверка результата

1. Откройте Adminer: [http://localhost:8080](http://localhost:8080)
2. Введите параметры подключения:

* **Система**: PostgreSQL
* **Сервер**: `db`
* **Пользователь**: значение из `.env` (например `postgres`)
* **Пароль**: значение из `.env` (например `postgres`)
* **База данных**: значение из `.env` (например `albion_craftflow`)

После входа вы должны увидеть созданные таблицы.

---

## 3. Сидинг данных (Seeding)

На этом этапе база данных наполняется справочными данными (города, базовые предметы и т.д.). Команда также выполняется внутри контейнера API.

### Команда

```bash
docker exec -it albion_api python -m src.scripts.seed_db
```

### Ожидаемый результат

```text
[INFO] - seed_db_script - Seeding locations...
[INFO] - seed_db_script - Locations seeded.
[INFO] - src.services.seeder - Starting bulk insert of items...
[INFO] - src.services.seeder - Items seeding completed.
```

---


