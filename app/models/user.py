from enum import Enum
from pydantic import EmailStr

from sqlmodel import Field
from app.models.base import BaseModel


class UserRole(str, Enum):
    USER = ("user",)
    MANAGER = "manager"


class User(BaseModel, table=True):  # type: ignore
    __tablename__ = "users"

    username: str = Field(unique=True, nullable=False)
    email: EmailStr = Field(nullable=False)
    password: str
    role: UserRole = Field(nullable=False, default_factory=UserRole.USER)
