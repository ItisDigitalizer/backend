import uuid

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.email_notification import EmailNotification


class EmailNotificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_log(
        self, recipient: str, subject: str, template_name: str, user_id: uuid.UUID | None = None
    ) -> EmailNotification:
        db_log = EmailNotification(
            recipient=recipient, subject=subject, template_name=template_name, status="pending", user_id=user_id
        )
        self.session.add(db_log)
        await self.session.commit()
        await self.session.refresh(db_log)
        return db_log

    async def update_status(self, log_id: uuid.UUID, status: str):
        db_log = await self.session.get(EmailNotification, log_id)
        if db_log:
            db_log.status = status
            self.session.add(db_log)
            await self.session.commit()
