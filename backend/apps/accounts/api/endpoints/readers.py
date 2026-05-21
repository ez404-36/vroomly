__all__ = (
    "UserAPI",
)

from fastapi import HTTPException
from fastapi_utils.cbv import cbv
from starlette import status

from apps.accounts.models.user import User
from common.orm.views.mixins import BaseAPI
from common.schemas.models import CurrentUser, UpdateUserProfile
from core.db import database

from ..routers import router


@cbv(router)
class UserAPI(
    BaseAPI,
):
    @router.get(
        "/me",
        summary="Получение информации о текущем пользователе",
        response_model=CurrentUser,
    )
    async def api_get_current_user(self) -> CurrentUser:
        return self.user

    @router.patch(
        "/me",
        summary="Обновление профиля текущего пользователя",
        response_model=CurrentUser,
    )
    async def api_update_current_user(self, data: UpdateUserProfile) -> CurrentUser:
        from sqlalchemy import select

        query = select(User).where(User.id == self.user.id)
        user = await database.fetch_one(query)

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        async with database.get_async_session() as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)

        return CurrentUser.model_validate(user)
