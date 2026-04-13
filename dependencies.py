from typing import Annotated

from fastapi import Depends, Request

from app.config import Settings
from app.services.user import UserService


def get_settings() -> Settings:
    return Settings()


def get_service(request: Request) -> UserService:
    return request.app.state.service


ServiceDep = Annotated[UserService, Depends(get_service)]
