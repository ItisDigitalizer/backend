from app.auth.utils import verify_password, create_access_token, hash_password
from app.schemas.authentication import LoginRequest
from app.repositories.user_repo import UserRepository


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def register(self, username: str, password: str):
        if self.user_repo.get_by_username(username):
            raise ValueError("User already exists")

        hashed = hash_password(password)
        return self.user_repo.create(username=username, password=hashed)

    def login(self, data: LoginRequest):
        user = self.user_repo.get_by_username(data.username)

        if not user or not verify_password(data.password, user.password):
            raise ValueError("Invalid credentials")

        token = create_access_token({"sub": str(user.id)})
        return {"access_token": token, "token_type": "bearer"}