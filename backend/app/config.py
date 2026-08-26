from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/city_anpr"
    REDIS_URL: str = "redis://localhost:6379/0"
    JWT_SECRET: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 480
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    UPLOAD_DIR: str = "./uploads"
    LOG_LEVEL: str = "INFO"
    APP_NAME: str = "City ANPR"
    DEBUG: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
