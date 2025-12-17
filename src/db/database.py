from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# ВАЖНО: Импортируем функцию получения настроек, а не объект
from src.config import get_settings

# Получаем настройки (вызовется один раз и закешируется)
settings = get_settings()

# 1. Создаем движок (Engine)
# Используем URL из настроек
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=(settings.MODE == "DEV")  # Логируем SQL только в режиме разработки
)

# 2. Создаем фабрику сессий (Session Maker)
# Именно эту переменную ищет твой скрипт seed_db.py!
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# 3. Базовый класс для моделей
class Base(DeclarativeBase):
    pass

# 4. Dependency для FastAPI (используется в роутерах)
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session