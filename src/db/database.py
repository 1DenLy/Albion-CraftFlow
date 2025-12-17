from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# функция получения настроек
from src.config import get_settings

# настройки
settings = get_settings()

# движок
# URL из настроек
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=(settings.MODE == "DEV")  # Логируем SQL только в режиме разработки
)

# Session Maker
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# Базовый класс для моделей
class Base(DeclarativeBase):
    pass


# Dependency для FastAPI (используется в роутерах)
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session