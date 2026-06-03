import asyncio
import os

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.auth.password_utils import hash_password
from app.models.user import User, UserRole

# Берём настройки БД из переменных окружения
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+asyncpg://{os.getenv('DB__USER', 'postgres')}:{os.getenv('DB__PASSWORD', 'admin')}@"
    f"{os.getenv('DB__HOST', 'localhost')}:{os.getenv('DB__PORT', '5432')}/{os.getenv('DB__NAME', 'testdig')}",
)


async def init_rbac():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        # Проверяем, есть ли хоть один менеджер
        result = await session.execute(select(User).where(User.role == UserRole.MANAGER))
        manager = result.scalar_one_or_none()

        if not manager:
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
            print("   password: admin123")
            print("   role: MANAGER")
            print("   is_verified: True")
        else:
            print(f"ℹАдминистратор уже существует: {manager.username} (is_verified={manager.is_verified})")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_rbac())
