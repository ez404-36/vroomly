from datetime import datetime, timezone
from uuid import UUID

import jwt
from fastapi import HTTPException
from sqlalchemy import select
from starlette import status

from apps.accounts.models.user_session import UserSession
from common.schemas.models import CurrentUser
from core.db import database
from core.safety.token import ALGORITHM, SECRET_KEY, TOKEN


async def decode_token(user_id: str) -> CurrentUser | None:
	from apps.accounts.models.user import User

	user = await database.fetch_one(select(User).where(User.id == UUID(user_id)))

	if not user:
		return None

	return CurrentUser.model_validate(user)


async def get_current_user(token: TOKEN) -> CurrentUser | None:
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail='Invalid credentials',
		headers={'WWW-Authenticate': 'Bearer'},
	)

	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		user_id = payload.get('sub')
		jti = payload.get('jti')
		if user_id is None or jti is None:
			raise credentials_exception
	except jwt.InvalidTokenError:
		raise credentials_exception

	session = await database.fetch_one(
		select(UserSession).where(UserSession.token_jti == jti),
	)
	if not session:
		raise credentials_exception

	if session.expires_at < datetime.now(timezone.utc):
		raise credentials_exception

	return await decode_token(str(user_id))
