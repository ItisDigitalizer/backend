from uuid import UUID

from app.models.authentication import RefreshSession
from app.repositories.base import Repository
from app.schemas.authentication import RefreshSessionFilters


class RefreshSessionRepository(Repository[RefreshSession]):
    model = RefreshSession

    async def revoke_session(self, jti: UUID):
        session = await self.fetch_one(RefreshSessionFilters(jti=jti))

        if not session:
            return None

        session.is_revoked = True

        return await self.save(session)
