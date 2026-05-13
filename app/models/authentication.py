import uuid
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import Column, ForeignKey, TIMESTAMP
from sqlmodel import Field, Relationship

from app.models import User
from app.models.base import BaseModel


class RefreshSession(BaseModel, table=True):
    __tablename__ = "refresh_sessions"

    user_id: UUID = Field(sa_column=Column(ForeignKey("users.id", ondelete="CASCADE")))

    user: "User" = Relationship(back_populates="sessions")

    jti: uuid.UUID = Field(
        unique=True,
        index=True,
        nullable=False,
    )

    expires_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_type=TIMESTAMP(timezone=True),  # type: ignore
    )

    revoked: bool = Field(
        default=False,
        nullable=False,
    )
