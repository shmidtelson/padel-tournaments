from datetime import UTC, datetime, timedelta
from typing import Any, cast

from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return cast(bool, pwd_context.verify(plain_password, hashed_password))


def get_password_hash(password: str) -> str:
    return cast(str, pwd_context.hash(password))


def _utc_now() -> datetime:
    return datetime.now(UTC)


def create_access_token(subject: str | int, extra: dict[str, Any] | None = None) -> str:
    expire = _utc_now() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    if extra:
        to_encode.update(extra)
    return cast(str, jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm))


def create_refresh_token(subject: str | int) -> str:
    expire = _utc_now() + timedelta(days=settings.refresh_token_expire_days)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    return cast(str, jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm))


def decode_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return cast("dict[str, Any] | None", payload)
    except JWTError:
        return None
