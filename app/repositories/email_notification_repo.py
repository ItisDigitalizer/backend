import uuid

from app.models.email_notification import EmailNotification
from app.repositories.base import Repository


class EmailNotificationRepository(Repository[EmailNotification]):
    async def create_log(
        self, recipient: str, subject: str, template_name: str, user_id: uuid.UUID | None = None
    ) -> EmailNotification:
        db_log = EmailNotification(
            recipient=recipient, subject=subject, template_name=template_name, status="pending", user_id=user_id
        )
        self._session.add(db_log)
        await self._session.commit()
        await self._session.refresh(db_log)
        return db_log

    async def update_status(self, log_id: uuid.UUID, status: str):
        db_log = await self._session.get(EmailNotification, log_id)
        if db_log:
            db_log.status = status
            self._session.add(db_log)
            await self._session.commit()
