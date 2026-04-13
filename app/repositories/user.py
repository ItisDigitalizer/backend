from sqlmodel import select, Session

from app.models import User

from collections.abc import Callable

from app.exceptions import NotFoundError

import sqlalchemy


class UserRepo:
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def get_users(self) -> list[User]:
        with self.session_factory() as session:
            return session.exec(select(User)).all()

    def get_user(self, id: int) -> User:
        with self.session_factory() as s:
            try:
                return s.exec(select(User).where(User.id == id)).one()
            except sqlalchemy.exc.NoResultFound:
                raise NotFoundError(f"User with {id=} not found")

    def create_user(self, user: User) -> User:
        with self.session_factory() as s:
            s.add(user)
            s.commit()
            return user
