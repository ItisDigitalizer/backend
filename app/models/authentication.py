from datetime import datetime
from uuid import UUID

from sqlalchemy import Column, ForeignKey
from sqlmodel import Field, Relationship

from app.models import User
from app.models.base import BaseModel


class RefreshSession(BaseModel, table=True):
    __tablename__ = "refresh_sessions"

    user_id: UUID = Field(
        sa_column=Column(
            ForeignKey("users.id", ondelete="CASCADE")
        )
    )

    user: "User" = Relationship(back_populates="sessions")

    jti: str = Field(
        unique=True,
        index=True,
        nullable=False,
    )

    expires_at: datetime = Field(nullable=False)

    revoked: bool = Field(
        default=False,
        nullable=False,
    )