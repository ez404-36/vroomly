__all__ = (
    'get_current_user',
    'request_user',
)

import jwt
from fastapi import HTTPException, status, Depends
from sqlalchemy import select

from apps.users.api.schemas.readers import UserDetail
from apps.users.models.user import UserModel
from config.database import get_async_session
from core.safety.token import TOKEN, SECRET_KEY, ALGORITHM, TokenData


async def decode_token(token: TokenData) -> UserDetail | None:
    async with get_async_session() as session:
        user_query = (
            select(UserModel)
            .where(UserModel.id == token.user_id)
        )
        user: UserModel = (await session.scalars(user_query)).one()

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
