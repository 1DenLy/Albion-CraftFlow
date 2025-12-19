from pydantic import BaseModel, Field


class IngestorConfig(BaseModel):
    """Конфигурация для сервиса сбора данных."""

    albion_api_url: str = Field(..., description="Базовый URL API Albion Online")
    max_rate: float = Field(default=1.0, gt=0, description="Максимальное кол-во запросов в секунду")
    concurrency: int = Field(default=1, ge=1, description="Макс. кол-во одновременных задач (для asyncio.gather)")
    request_timeout: float = Field(default=10.0, gt=0, description="Timeout HTTP запроса в секундах")
    batch_size: int = Field(default=50, ge=1, le=100, description="Кол-во предметов в одном запросе (во избежание 414 URI Too Long)")