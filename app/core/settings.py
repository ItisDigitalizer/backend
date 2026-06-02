from functools import lru_cache

from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    driver: str
    host: str
    user: str
    password: str
    port: int
    name: str


class AuthSettings(BaseSettings):
    secret_key: str
    algorithm: str

    access_token_expire_minutes: int
    refresh_token_expire_days: int


class SMTPSettings(BaseSettings):
    username: str
    password: str
    mail_from: EmailStr
    port: int
    server: str
    starttls: bool = False
    ssl_tls: bool = True


class Settings(BaseSettings):
    db: DatabaseSettings
    auth: AuthSettings
    smtp: SMTPSettings

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_nested_delimiter="__",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
