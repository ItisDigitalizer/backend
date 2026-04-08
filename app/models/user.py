from enum import Enum
from pydantic import BaseModel
from datetime import datetime


class UserRole(str, Enum):
    USER = ("user",)
    MANAGER = ("manager",)


class User(BaseModel):
    id: int
    username: str
    email: str
    password_hash: str
    role: UserRole = UserRole.USER
    created_at: datetime = datetime.now()
