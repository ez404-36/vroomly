__all__ = (
    'authenticate_user',
)

from fastapi import HTTPException
from sqlalchemy import select, and_, or_

from apps.accounts.models.user import User
from config.database import get_async_session
from core.safety.token import TokenData, verify_password


async def authenticate_user(username: str, password: str) -> TokenData | None:
    async with get_async_session() as session:
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
        user: User = (await session.scalars(user_query)).one()

    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    if not verify_password(password, user.password_hash):
        return None

    return TokenData(user_id=str(user.id))
