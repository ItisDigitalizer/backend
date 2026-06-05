import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.auth.password_utils import hash_password
from app.db.database import form_db_url
from app.models.user import User, UserRole


async def init_rbac():
    DATABASE_URL = form_db_url()
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        result = await session.execute(select(User).where(User.role == UserRole.MANAGER))
        managers = result.scalars().all()

        if not managers:
            # Создаём верифицированного администратора
            admin = User(
                username="admin",
                email="admin@example.com",
                password=hash_password("admin123"),
                role=UserRole.MANAGER,
                is_verified=True,
            )
            session.add(admin)
            await session.commit()
            print("   Создан ВЕРИФИЦИРОВАННЫЙ администратор:")
            print("   username: admin")

        else:
            print(f"Уже есть {len(managers)} менеджеров")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_rbac())
