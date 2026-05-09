import re

from pydantic import BaseModel, EmailStr, field_validator
from sqlmodel import SQLModel

from app.models.user import UserBase, UserRole


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(UserBase):
    password: str


class UserFilters(SQLModel):
    username: str | None = None
    email: str | None = None
    role: UserRole | None = None

    class Config:
        from_attributes = True


class UserOut(BaseModel):
    id: int
    email: EmailStr
