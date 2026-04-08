from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Digitalizer"
    DEBUG: bool = True
    UPLOAD_DIR: str = "uploads"
    TEMPLATES_DIR: str = "templates"
    DATABASE_URL: str = "sqlite:///./digitalizer.db"

    class Config:
        env_file = ".env"
