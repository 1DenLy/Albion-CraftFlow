from functools import lru_cache
from typing import Literal
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- ОБЩИЕ НАСТРОЙКИ ---
    MODE: Literal["DEV", "TEST", "PROD"] = "DEV"
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"


    # --- НАСТРОЙКИ БАЗЫ ДАННЫХ (PostgreSQL) ---
    DB_HOST: str
    DB_PORT: int = 5432
    DB_USER: str
    DB_PASS: SecretStr
    DB_NAME: str


    # SEEDING (Наполнение базы) ---
    SEED_ITEMS_URL: str = "https://raw.githubusercontent.com/broderickhyman/ao-bin-dumps/master/formatted/items.json"
    SEED_MIN_TIER: int = 4
    SEED_MAX_TIER: int = 8
    ENABLE_TRACKING_SEEDING: bool = True

    # Albion API Settings
    ALBION_API_URL: str = "https://europe.albion-online-data.com/api/v2/stats/prices"

    # Ingestor Settings
    INGESTOR_BATCH_SIZE: int = 50
    INGESTOR_CONCURRENCY: int = 1
    INGESTOR_RATE_LIMIT: float = 0.60
    INGESTOR_SLEEP_SEC: int = 30


    @property
    def DATABASE_URL(self) -> str:
        """
        Собирает DSN строку для SQLAlchemy асинхронно.
        """
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS.get_secret_value()}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


    # --- КОНФИГУРАЦИЯ ЗАГРУЗКИ ---
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )



@lru_cache
def get_settings() -> Settings:
    return Settings()