# app/repositories/user_repo.py
from typing import Optional, Sequence

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.user import User
from app.repositories.base import Repository
from app.schemas.user import UserFilters


class UserRepository(Repository[User]):
    model = User

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_email(self, email: str) -> Optional[User]:
        filters = UserFilters(email=email)
        result = await self.fetch(filters)
        return result[0] if result else None

    async def get_by_username(self, username: str) -> Optional[User]:
        filters = UserFilters(username=username)
        result = await self.fetch(filters)
        return result[0] if result else None

    async def fetch_with_filters(
        self, filters: UserFilters, offset: int = 0, limit: int = 100
    ) -> Sequence[User]:
        return await self.fetch(filters, offset, limit)
