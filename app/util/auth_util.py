from app.config import settings
from datetime import datetime, UTC, timedelta
from pydantic import SecretStr

import jwt

from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from .string_util import str_decode, str_encode


password_hasher = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")


def hash_password(plain_pwd: str) -> str:
    return password_hasher.hash(plain_pwd)


def verify_password(plain_pwd: str, hashed_pwd: str) -> bool:
    return password_hasher.verify(plain_pwd, hashed_pwd)


def create_access_token(sub: str) -> str:
    sub = str_encode(sub)
    expires_at = datetime.now(tz=UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    data = {"sub": sub, "exp": expires_at}
    return _create_access_or_refresh_token(data, _key=settings.access_token_secret_key)


def create_refresh_token(sub: str) -> str:
    sub = str_encode(sub)
    expires_at = datetime.now(tz=UTC) + timedelta(days=settings.refresh_token_expire_days)
    data = {"sub": sub, "exp": expires_at}
    return _create_access_or_refresh_token(data, _key=settings.refresh_token_secret_key)


def _create_access_or_refresh_token(data: dict, _key: SecretStr) -> str:
    to_encode = data.copy()
    jwt_encoded = jwt.encode(
        payload=to_encode,
        key=_key.get_secret_value(),
        algorithm=settings.jwt_algorithm
    )
    return jwt_encoded


def verify_access_token(token: str) -> str | None:
    return _verify_access_or_refresh_token(token, _key=settings.access_token_secret_key)


def verify_refresh_token(token: str) -> str | None:
    return _verify_access_or_refresh_token(token, _key=settings.refresh_token_secret_key)


def _verify_access_or_refresh_token(token: str, _key: SecretStr) -> str | None:
    try:
        payload = jwt.decode(
            jwt=token,
            key=_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "exp"]}
        )
    except jwt.InvalidTokenError:
        return None
    else:
        return payload
