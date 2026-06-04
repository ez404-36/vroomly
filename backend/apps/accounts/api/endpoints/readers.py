__all__ = ('UserAPI',)

from fastapi import HTTPException
from fastapi_utils.cbv import cbv
from starlette import status

from apps.accounts.services.profile import ProfileService
from common.orm.views.mixins import BaseAPI
from common.schemas.models import CurrentUser, UpdateUserProfile

from ..routers import router


@cbv(router)
class UserAPI(
	BaseAPI,
):
	"""API чтения и обновления профиля текущего пользователя."""

	@router.get(
		'/me',
		summary='Получение информации о текущем пользователе',
		response_model=CurrentUser,
	)
	async def api_get_current_user(self) -> CurrentUser:
		"""Вернуть информацию о текущем пользователе."""
		return self.user

	@router.patch(
		'/me',
		summary='Обновление профиля текущего пользователя',
		response_model=CurrentUser,
	)
	async def api_update_current_user(self, data: UpdateUserProfile) -> CurrentUser:
		"""Обновить профиль текущего пользователя."""
		user = await ProfileService().update(self.user.id, data)
		if user is None:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
		return CurrentUser.model_validate(user)
