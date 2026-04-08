from fastapi import Request

from app.config import Settings


from app.service import Service


def get_settings() -> Settings:
    return Settings()


def get_service(request: Request) -> Service:
    return request.app.state.service
