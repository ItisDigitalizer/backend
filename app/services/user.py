from app.models import User
from app.repositories.user import UserRepo


class UserService:
    def __init__(self, repo: UserRepo):
        self.repo = repo

    def get_users(self) -> list[User]:
        return self.repo.get_users()

    def get_user(self, id: int) -> User:
        return self.repo.get_user(id)

    def create_user(self, user: User) -> User:
        return self.repo.create_user(user)
