from datetime import datetime, timedelta, timezone
from typing import Annotated, TypeAlias
from uuid import uuid4

import bcrypt
import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/accounts/login')
TOKEN: TypeAlias = Annotated[str, Depends(oauth2_scheme)]

SECRET_KEY = '5ac60563c2608c2140df347ff80722682689df27833cd7289bf3bfc6863128b9'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 5

# Bcrypt cost factor (12 is the default, matches what's in User model)
BCRYPT_COST: int = 12


class Token(BaseModel):
	access_token: str
	token_type: str


class TokenData(BaseModel):
	user_id: str | None
	jti: str | None


def verify_password(plain_password: str, hashed_password: str) -> bool:
	"""Verify a plain password against a hashed password."""
	return bcrypt.checkpw(
		plain_password.encode('utf-8'),
		hashed_password.encode('utf-8'),
	)


def get_password_hash(password: str) -> str:
	"""Generate a bcrypt hash for a password."""
	return bcrypt.hashpw(
		password.encode('utf-8'),
		bcrypt.gensalt(rounds=BCRYPT_COST),
	).decode('utf-8')


def decode_token_claims(token: str) -> tuple[str, datetime]:
	"""Извлечь ``jti`` и время истечения из JWT (без проверки подписи).

	:returns: кортеж ``(jti, expires_at)``. Если в токене нет ``jti`` —
		возвращается пустая строка; если нет ``exp`` — берётся время истечения
		по умолчанию (``ACCESS_TOKEN_EXPIRE_MINUTES`` от текущего момента).
	"""
	payload = jwt.decode(token, options={'verify_signature': False})
	jti = payload.get('jti') or ''
	exp = payload.get('exp')
	expires_at = datetime.fromtimestamp(exp, tz=timezone.utc) if exp else _default_token_expiry()
	return jti, expires_at


def _default_token_expiry() -> datetime:
	"""Время истечения токена по умолчанию (``ACCESS_TOKEN_EXPIRE_MINUTES`` от now)."""
	return datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
	"""Create a JWT access token with a unique jti claim."""
	to_encode = data.copy()
	expires_delta = expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
	expire = datetime.now(timezone.utc) + expires_delta
	to_encode.update(
		{
			'exp': expire,
			'jti': str(uuid4()),
		}
	)
	encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
	return encoded_jwt
