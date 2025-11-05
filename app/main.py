# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
import logging

from app.database import AsyncSessionLocal, engine

from .routers import items

# Настройка логирования (чтобы видеть ошибки в консоли)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="My Project")
app.include_router(items.router)


# 1. Зависимость (dependency) для получения сессии БД
async def get_db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


# 2. Простой эндпоинт, чтобы проверить, что сервер работает
@app.get("/")
async def read_root():
    return {"message": "Привет! Сервер FastAPI работает."}


# 3. Эндпоинт для ПРОВЕРКИ ПОДКЛЮЧЕНИЯ к базе Supabase
@app.get("/test-db")
async def test_database_connection(session: AsyncSession = Depends(get_db_session)):
    try:
        # Выполняем простой SQL-запрос, чтобы проверить связь
        # text() нужен, чтобы SQLAlchemy понял, что это "сырой" SQL
        result = await session.execute(text("SELECT 1"))

        if result.scalar() == 1:
            logger.info("✅ Успешное подключение к базе данных Supabase!")
            return {"status": "success", "message": "Подключение к базе данных Supabase успешно!"}
        else:
            raise HTTPException(status_code=500, detail="Неожиданный результат от БД")

    except Exception as e:
        logger.error(f"❌ ОШИБКА подключения к базе данных: {e}")
        # Если будет ошибка (неверный пароль, хост, firewall), мы упадем сюда
        raise HTTPException(status_code=500, detail=f"Ошибка подключения к базе данных: {str(e)}")