from typing import Annotated

from fastapi.params import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session
from app.repositories.user_repo import UserRepository
from app.services.user_service import UserService

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session)


def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(repository)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
