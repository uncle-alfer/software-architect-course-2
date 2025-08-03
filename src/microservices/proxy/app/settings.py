from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field, AnyHttpUrl


class Settings(BaseSettings):
    # Port FastAPI будет слушать внутри контейнера
    PORT: int = 8000

    # Бэкенды
    MONOLITH_URL:        AnyHttpUrl = Field("http://monolith:8080", env="MONOLITH_URL")
    MOVIES_SERVICE_URL:  AnyHttpUrl = Field("http://movies-service:8081", env="MOVIES_SERVICE_URL")
    EVENTS_SERVICE_URL:  AnyHttpUrl = Field("http://events-service:8082", env="EVENTS_SERVICE_URL")

    # Фича-флаг миграции
    GRADUAL_MIGRATION:       bool = Field(True, env="GRADUAL_MIGRATION")
    MOVIES_MIGRATION_PERCENT: int  = Field(50, env="MOVIES_MIGRATION_PERCENT")  # 0-100

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()
