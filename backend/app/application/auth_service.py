"""Application service: authentication and user registration."""

from app.domain.entities import User
from app.domain.repositories import IUserRepository
from app.application.dto import RegisterUserCommand, LoginResult
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)


class AuthApplicationService:
    def __init__(self, user_repository: IUserRepository):
        self._users = user_repository

    async def register_email(self, email: str, password: str, first_name: str | None = None, last_name: str | None = None) -> User:
        existing = await self._users.get_by_email(email)
        if existing:
            raise ValueError("User with this email already exists")
        user = User(
            id=0,
            email=email,
            phone=None,
            telegram_id=None,
            first_name=first_name,
            last_name=last_name,
            password_hash=get_password_hash(password),
        )
        return await self._users.add(user)

    async def login_email(self, email: str, password: str) -> LoginResult:
        user = await self._users.get_by_email(email)
        if not user or not user.password_hash:
            raise ValueError("Invalid email or password")
        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")
        access = create_access_token(user.id)
        refresh = create_refresh_token(user.id)
        return LoginResult(user_id=user.id, access_token=access, refresh_token=refresh)

    async def refresh_tokens(self, refresh_token: str) -> LoginResult:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")
        user_id = int(payload["sub"])
        user = await self._users.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        return LoginResult(
            user_id=user.id,
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self._users.get_by_id(user_id)
