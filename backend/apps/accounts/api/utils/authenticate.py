__all__ = (
    'authenticate_user',
)

from fastapi import HTTPException
from sqlalchemy import and_, or_, select
from starlette import status

from apps.accounts.models.user import User
from core.db import database
from core.safety.token import verify_password


async def authenticate_user(username: str, password: str) -> User | None:
    user_query = select(User).where(
        and_(
            or_(
                User.login == username,
                User.email == username,
            ),
            User.deleted.isnot(True),
        )
    )
    user: User = await database.fetch_one(user_query)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    if not verify_password(password, user.password_hash):
        return None

    return user