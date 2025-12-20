from pydantic import Field
from pydantic_settings import BaseSettings


class IngestorConfig(BaseSettings):
    """Configuration for the Ingestor service."""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    albion_api_url: str = Field(..., description="Albion Online API base URL")
    max_rate: float = Field(default=0.50, gt=0, description="Maximum number of requests per second")
    concurrency: int = Field(default=1, ge=1, description="Maximum number of simultaneous tasks (for asyncio.gather)")
    request_timeout: float = Field(default=10.0, gt=0, description="HTTP request timeout in seconds")
    batch_size: int = Field(default=50, ge=1, le=100, description="Number of items in a single request (to avoid 414 URI Too Long)")