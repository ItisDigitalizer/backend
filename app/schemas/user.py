import uuid

from sqlmodel import SQLModel

from app.models.user import UserRole


class UserFilters(SQLModel):
    id: uuid.UUID | None = None
    username: str | None = None
    email: str | None = None
    role: UserRole | None = None

    class Config:
        from_attributes = True
