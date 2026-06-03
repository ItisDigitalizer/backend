import uuid
from pathlib import Path

from fastapi import BackgroundTasks, Depends
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from app.core.settings import settings
from app.db.session import async_session_maker
from app.repositories.email_notification_repo import EmailNotificationRepository

conf = ConnectionConfig(
    MAIL_USERNAME=settings.smtp.username,
    MAIL_PASSWORD=settings.smtp.password,
    MAIL_FROM=settings.smtp.mail_from,
    MAIL_PORT=settings.smtp.port,
    MAIL_SERVER=settings.smtp.server,
    MAIL_STARTTLS=settings.smtp.starttls,
    MAIL_SSL_TLS=settings.smtp.ssl_tls,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
    # SUPPRESS_SEND=1,
)

fastmail = FastMail(conf)


class EmailService:
    def __init__(
        self,
        repo: EmailNotificationRepository = Depends(),
    ):
        self.email_notification_repository = repo

    @staticmethod
    async def _send_async(message: MessageSchema, template_name: str):
        try:
            await fastmail.send_message(message, template_name=template_name)
            return "sent"
        except Exception as e:
            print(f"SMTP Error: {e}")
            return "failed"

    def send_background_email(
        self,
        background_tasks: BackgroundTasks,
        email: EmailStr,
        subject: str,
        template_name: str,
        context: dict,
        user_id: uuid.UUID | None = None,
    ):
        message = MessageSchema(subject=subject, recipients=[email], template_body=context, subtype=MessageType.html)

        async def task_wrapper():
            async with async_session_maker() as background_session:
                self.email_notification_repository.session = background_session

                log_entry = await self.email_notification_repository.create_log(
                    recipient=email, subject=subject, template_name=template_name, user_id=user_id
                )

                status = await self._send_async(message, template_name=template_name)

                await self.email_notification_repository.update_status(log_entry.id, status)

        background_tasks.add_task(task_wrapper)
