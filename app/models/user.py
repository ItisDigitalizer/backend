from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel


class UserRole(str, Enum):
    USER = ("user",)
    MANAGER = ("manager",)


class User(SQLModel, table=True):  # type: ignore
    __tablename__ = "users"

    id: int | None = Field(primary_key=True, default=None)
    username: str = Field(unique=True, nullable=False)
    email: str = Field(nullable=False)
    password_hash: str
    role: UserRole = Field(nullable=False, default_factory=UserRole.USER)
    created_at: datetime = Field(default_factory=datetime.now)
