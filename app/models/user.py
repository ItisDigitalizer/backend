import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.document_template import DocumentTemplate
    from app.models.generation_process import GenerationProcess


class UserRole(str, Enum):
    USER = "user"
    MANAGER = "manager"


class User(BaseModel, table=True):  # type: ignore
    __tablename__ = "users"

    username: str = Field(unique=True, nullable=False)
    email: EmailStr = Field(nullable=False)
    password: str
    role: UserRole = Field(nullable=False, default=UserRole.USER)

    templates: List["DocumentTemplate"] = Relationship(back_populates="user")
    processes: List["GenerationProcess"] = Relationship(back_populates="user")


class UserBase(SQLModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.USER


class UserCreate(UserBase):
    pass


class UserUpdate(SQLModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    role: UserRole | None = None


class UserRead(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
