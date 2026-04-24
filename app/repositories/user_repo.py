# app/repositories/user_repo.py
from typing import Optional, Sequence

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.user import User
from app.repositories.base import Repository
from app.schemas.user import UserFilters


class UserRepository(Repository[User]):
    model = User

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Поиск пользователя по email"""
        statement = select(self.model).where(self.model.email == email)
        result = await self._session.exec(statement)
        return result.first()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Поиск пользователя по username"""
        statement = select(self.model).where(self.model.username == username)
        result = await self._session.exec(statement)
        return result.first()

    async def fetch_with_filters(
        self, filters: UserFilters, offset: int = 0, limit: int = 100
    ) -> Sequence[User]:
        return await self.fetch(filters, offset, limit)
