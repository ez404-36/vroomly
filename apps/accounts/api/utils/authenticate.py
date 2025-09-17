__all__ = (
    'authenticate_user',
)

from fastapi import HTTPException
from sqlalchemy import select, and_, or_

from apps.accounts.models.user import User
from core.db import database
from core.safety.token import TokenData, verify_password


async def authenticate_user(username: str, password: str) -> TokenData | None:
    user_query = (
        select(User)
        .where(
            and_(
                or_(
                    User.login == username,
                    User.email == username,
                ),
                User.deleted.isnot(True),
            )
        )
    )
    user: User = await database.fetch_one(user_query)

    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    if not verify_password(password, user.password_hash):
        return None

    return TokenData(user_id=str(user.id))
