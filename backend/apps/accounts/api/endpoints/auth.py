from typing import Annotated

from fastapi import Depends, Form, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_utils.cbv import cbv
from starlette import status

from apps.accounts.api.routers import router
from apps.accounts.api.schemas.mutators import RegistrationDataForm
from apps.accounts.services.auth import AuthService
from common.auth.decode_token import get_current_user
from common.schemas.models import CurrentUser
from core.safety.token import Token


@cbv(router)
class UserAuthAPI:
	"""API аутентификации, выхода и регистрации пользователей."""

	@router.post(
		'/login',
		summary='Аутентификация пользователя',
	)
	async def api_login(self, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
		"""Аутентифицировать пользователя и вернуть access-токен."""
		token = await AuthService().login(form_data.username, form_data.password)
		if token is None:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
		return token

	@router.post(
		'/logout',
		summary='Выход из системы',
		status_code=status.HTTP_200_OK,
	)
	async def api_logout(
		self,
		current_user: Annotated[CurrentUser | None, Depends(get_current_user)],
	) -> dict[str, str]:
		"""Завершить все сессии текущего пользователя."""
		if current_user is None:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authenticated')

		await AuthService().logout(current_user.id)
		return {'message': 'Successfully logged out'}

	@router.post(
		'/registration',
		status_code=status.HTTP_201_CREATED,
		summary='Регистрация пользователя',
		response_model=str,
	)
	async def api_registration(self, data: Annotated[RegistrationDataForm, Form()]) -> str:
		"""Зарегистрировать нового пользователя."""
		await AuthService().register(data)
		return 'ok'
