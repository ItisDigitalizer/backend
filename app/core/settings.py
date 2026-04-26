from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    db_schema: str = "postgresql+asyncpg"
    db_host: str = "localhost"
    db_user: str = "postgres"
    db_password: str = "admin"
    db_port: int = 5432
    db_name: str = "testdig"
    secret_key: str = "somekey"
    algorithm = "HS256"
    access_token_expire_minutes = 30

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
