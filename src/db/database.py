from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

# Создаем движок, используя готовый URL из settings
# echo=True включаем только если мы в режиме DEV
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=(settings.MODE == "DEV")
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# Базовый класс моделей
class Base(DeclarativeBase):
    pass

# Dependency для FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session