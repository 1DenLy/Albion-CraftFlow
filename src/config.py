from typing import Literal
from pydantic import SecretStr, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- ОБЩИЕ НАСТРОЙКИ ПРИЛОЖЕНИЯ ---
    # Literal ограничивает выбор только этими значениями
    MODE: Literal["DEV", "TEST", "PROD"] = "DEV"
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # --- НАСТРОЙКИ БАЗЫ ДАННЫХ (PostgreSQL) ---
    DB_HOST: str
    DB_PORT: int = 5432
    DB_USER: str
    DB_PASS: SecretStr # SecretStr скроет значение в логах (отобразится как '**********')
    DB_NAME: str

    @property
    def DATABASE_URL(self) -> str:
        """
        Собирает DSN строку для SQLAlchemy асинхронно.
        Использование свойства позволяет менять части URL динамически, если нужно.
        """
        # get_secret_value() нужен, чтобы достать строку из SecretStr
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS.get_secret_value()}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # --- БУДУЩИЕ НАСТРОЙКИ (Раскомментируй по мере необходимости) ---

    # 1. REDIS (Для кэширования и брокера задач Celery)
    # REDIS_HOST: str = "localhost"
    # REDIS_PORT: int = 6379
    # @property
    # def REDIS_URL(self) -> str:
    #     return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    # 2. AUTH (JWT Токены)
    # Генерация случайного ключа: openssl rand -hex 32
    # SECRET_KEY: SecretStr
    # ALGORITHM: str = "HS256"
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 3. SENTRY (Мониторинг ошибок в проде)
    # SENTRY_DSN: str | None = None

    # --- КОНФИГУРАЦИЯ ЗАГРУЗКИ ---
    model_config = SettingsConfigDict(
        env_file=".env",            # Имя файла с переменными
        env_file_encoding="utf-8",  # Кодировка
        extra="ignore"              # Игнорировать лишние переменные в .env (не падать ошибкой)
    )

# Инициализируем настройки один раз при импорте модуля
settings = Settings()