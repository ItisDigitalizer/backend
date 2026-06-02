import uuid
from pathlib import Path

from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.settings import settings

# Импортируем твою фабрику сессий
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
    @staticmethod
    async def _send_async(message: MessageSchema, template_name: str):
        try:
            await fastmail.send_message(message, template_name=template_name)
            return "sent"
        except Exception as e:
            print(f"SMTP Error: {e}")
            return "failed"

    @classmethod
    def send_background_email(  # !!! УБРАЛИ async КЛЮЧЕВОЕ СЛОВО !!!
        cls,
        background_tasks: BackgroundTasks,
        session: AsyncSession,
        email: EmailStr,
        subject: str,
        template_name: str,
        context: dict,
        user_id: uuid.UUID | None = None,
    ):
        # 1. Мы не можем использовать await внутри синхронной функции для создания лога.
        # Поскольку у нас асинхронная сессия, мы переносим создание лога внутрь самой фоновой задачи!

        message = MessageSchema(subject=subject, recipients=[email], template_body=context, subtype=MessageType.html)

        # 2. Обертка для фоновой задачи
        async def task_wrapper():
            # Открываем чистую асинхронную сессию
            async with async_session_maker() as background_session:
                background_repo = EmailNotificationRepository(background_session)

                # Создаем лог прямо тут, в фоне
                log_entry = await background_repo.create_log(
                    recipient=email, subject=subject, template_name=template_name, user_id=user_id
                )

                # Отправляем письмо
                status = await cls._send_async(message, template_name=template_name)

                # Обновляем статус
                await background_repo.update_status(log_entry.id, status)

        # 3. Передаем задачу в FastAPI воркер
        background_tasks.add_task(task_wrapper)
