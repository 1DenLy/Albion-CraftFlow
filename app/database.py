from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config import settings # Импортируем наши настройки

# Создаем асинхронный "движок"
engine = create_async_engine(
    settings.DATABASE_URL
)

# Создаем фабрику сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db_session():
    """
    Dependency (зависимость) для получения сессии БД.
    Открывает сессию, "выдает" ее эндпоинту и гарантированно
    закрывает ее после завершения, даже если была ошибка.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()