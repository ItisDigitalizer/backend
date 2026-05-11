from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    db_schema: str
    db_host: str
    db_user: str
    db_password: str
    db_port: int
    db_name: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


class AuthSettings(BaseSettings):
    secret_key: str
    algorithm: str

    access_token_expire_minutes: int
    refresh_token_expire_days: int

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


class Settings:
    db = DatabaseSettings()
    auth = AuthSettings()


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
