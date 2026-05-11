from enum import Enum
from typing import TYPE_CHECKING, List

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.document_template import DocumentTemplate
    from app.models.generation_process import GenerationProcess
    from app.models.authentication import RefreshSession


class UserRole(str, Enum):
    USER = "user"
    MANAGER = "manager"


class UserBase(SQLModel):
    username: str = Field(unique=True, nullable=False)
    email: EmailStr = Field(nullable=False)

    role: UserRole = Field(nullable=False, default=UserRole.USER)


class User(BaseModel, UserBase, table=True):
    __tablename__ = "users"
    password: str
    templates: List["DocumentTemplate"] = Relationship(back_populates="user")
    processes: List["GenerationProcess"] = Relationship(back_populates="user")
    sessions: list["RefreshSession"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete"}
    )


class UserCreate(UserBase):
    password: str


class UserUpdate(SQLModel):
    username: str | None = None
    email: EmailStr | None = None
    role: UserRole | None = None


class UserRead(UserBase, BaseModel):
    pass