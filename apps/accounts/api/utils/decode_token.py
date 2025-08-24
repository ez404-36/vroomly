__all__ = (
    'get_current_user',
    'request_user',
)

import jwt
from fastapi import HTTPException, status, Depends
from sqlalchemy import select

from apps.accounts.api.schemas.readers import UserDetail
from apps.accounts.models.user import User
from core.db import database
from core.safety.token import TOKEN, SECRET_KEY, ALGORITHM, TokenData


async def decode_token(token: TokenData) -> UserDetail | None:
    user = await database.fetch_one(
        select(User)
        .where(User.id == token.user_id)
    )

    if not user:
        return None

    return UserDetail.model_validate(user)


async def get_current_user(token: TOKEN) -> UserDetail:
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


request_user: UserDetail = Depends(get_current_user)
