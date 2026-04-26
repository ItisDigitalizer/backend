from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import settings


def form_db_url() -> str:
    return URL.create(
        drivername=settings.db_schema,
        username=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    ).render_as_string(hide_password=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


engine = create_async_engine(form_db_url(), echo=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
