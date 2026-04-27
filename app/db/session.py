from typing import Annotated

from database import engine
from fastapi import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession


async def get_session():
    async with AsyncSession(engine) as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
