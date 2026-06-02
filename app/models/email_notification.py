import uuid

from pydantic import EmailStr
from sqlmodel import Field

from .base import BaseModel


class EmailNotification(BaseModel, table=True):
    __tablename__ = "email_notifications"

    recipient: EmailStr = Field(nullable=False, index=True)
    subject: str = Field(nullable=False)
    template_name: str = Field(nullable=False)
    status: str = Field(default="pending", nullable=False)  # pending, sent, failed

    # Можно связать с пользователем, если необходимо:
    user_id: uuid.UUID | None = Field(default=None, foreign_key="users.id", nullable=True)
