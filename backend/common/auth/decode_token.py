from typing import TYPE_CHECKING

import jwt
from fastapi import HTTPException
from sqlalchemy import select
from starlette import status

from common.schemas.models import CurrentUser
from common.utils.file_inspectors import import_class
from core.db import database
from core.safety.token import ALGORITHM, SECRET_KEY, TOKEN, TokenData
from core.settings import settings

if TYPE_CHECKING:
	from apps.accounts.models.user import User


async def decode_token(token: TokenData) -> CurrentUser | None:
	user_model: 'User' = import_class(settings.user_model)
	user = await database.fetch_one(select(user_model).where(user_model.id == token.user_id))

	if not user:
		return None

	return CurrentUser.model_validate(user)


async def get_current_user(token: TOKEN) -> CurrentUser | None:
	credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		user_id = payload.get("sub")
		if user_id is None:
			raise credentials_exception
		token_data = TokenData(user_id=str(user_id))
	except jwt.InvalidTokenError:
		raise credentials_exception
	else:
		return await decode_token(token_data)
