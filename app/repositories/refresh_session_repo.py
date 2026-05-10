from sqlmodel import select

from app.models.authentication import RefreshSession
from app.repositories.base import Repository


class RefreshSessionRepository(Repository[RefreshSession]):
    model = RefreshSession

    async def get_by_jti(self, jti: str) -> RefreshSession | None:
        statement = select(RefreshSession).where(
            RefreshSession.jti == jti
        )

        result = await self._session.exec(statement)

        return result.first()

    async def revoke_by_jti(self, jti: str) -> bool:
        statement = select(RefreshSession).where(
            RefreshSession.jti == jti
        )

        result = await self._session.exec(statement)
        session = result.first()

        if not session:
            return False

        session.revoked = True

        self._session.add(session)
        await self._session.commit()
        await self._session.refresh(session)

        return True