# app/schemas/user.py
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class UserFilters(BaseModel):
    username: str | None = None
    email: str | None = None
    role: UserRole | None = None


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    role: UserRole
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
