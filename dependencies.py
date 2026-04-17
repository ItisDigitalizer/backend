from typing import Annotated

from fastapi import Depends, Request
from sqlmodel import create_engine

from app.config import Settings
from app.services.user import UserService


def get_settings() -> Settings:
    return Settings()


def get_service(request: Request) -> UserService:
    return request.app.state.service


ServiceDep = Annotated[UserService, Depends(get_service)]

engine = create_engine(
    get_settings().DATABASE_URL, connect_args={"check_same_thread": False}
)
