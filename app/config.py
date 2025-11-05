from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str

    # Указываем, что нужно прочитать файл .env
    model_config = SettingsConfigDict(env_file=".env")
    # (../.env потому что config.py лежит в папке app, а .env - снаружи)

settings = Settings()