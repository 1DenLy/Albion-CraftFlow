from pydantic import Field
from pydantic_settings import BaseSettings # pip install pydantic-settings


class IngestorConfig(BaseSettings):
    """Конфигурация для сервиса сбора данных."""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    albion_api_url: str = Field(..., description="Базовый URL API Albion Online")
    max_rate: float = Field(default=0.50, gt=0, description="Максимальное кол-во запросов в секунду")
    concurrency: int = Field(default=1, ge=1, description="Макс. кол-во одновременных задач (для asyncio.gather)")
    request_timeout: float = Field(default=10.0, gt=0, description="Timeout HTTP запроса в секундах")
    batch_size: int = Field(default=50, ge=1, le=100, description="Кол-во предметов в одном запросе (во избежание 414 URI Too Long)")