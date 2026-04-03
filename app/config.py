from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Digitalizer"
    DEBUG: bool = True
    UPLOAD_DIR: str = "uploads"
    TEMPLATES_DIR: str = "templates"

    class Config:
        env_file = ".env"


settings = Settings()
