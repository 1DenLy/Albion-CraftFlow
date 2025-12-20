from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from src.config import get_settings

# get settings from config
settings = get_settings()

# engine
# URL from settings
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=(settings.MODE == "DEV")  # Logs SQL only in DEV mode
)

# Session Maker
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# Base Model Class
class Base(DeclarativeBase):
    pass


# Dependency для FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session