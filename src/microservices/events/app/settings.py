from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PORT: int = 8082
    KAFKA_BROKERS: str = "kafka:9092"
    TOPIC_USERS: str     = "user-events"
    TOPIC_MOVIES: str    = "movie-events"
    TOPIC_PAYMENTS: str  = "payment-events"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

def get_settings() -> Settings:
    return Settings()
