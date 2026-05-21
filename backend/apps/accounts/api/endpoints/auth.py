from typing import Annotated

from fastapi import Depends, Form, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_utils.cbv import cbv
from starlette import status

from apps.accounts.api.routers import router
from apps.accounts.api.schemas.mutators import RegistrationDataForm
from apps.accounts.api.utils import authenticate_user
from apps.accounts.models.user import User
from apps.accounts.models.user_session import UserSession
from common.auth.decode_token import get_current_user
from common.schemas.models import CurrentUser
from core.db import database
from core.safety.token import Token, create_access_token


@cbv(router)
class UserAuthAPI:
	@router.post(
		'/login',
		summary='Аутентификация пользователя',
	)
	async def api_login(self, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
		user = await authenticate_user(form_data.username, form_data.password)

		if not user:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

		access_token = create_access_token(
			data={'sub': str(user.id)},
		)

		session = UserSession.create_from_token(user_id=user.id, token=access_token)
		async with database.get_async_session() as session_ctx:
			session_ctx.add(session)
			await session_ctx.commit()

		return Token(access_token=access_token, token_type='bearer')

	@router.post(
		'/logout',
		summary='Выход из системы',
		status_code=status.HTTP_200_OK,
	)
	async def api_logout(self, current_user: Annotated[CurrentUser | None, Depends(get_current_user)]):
		if current_user is None:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authenticated')

		async with database.get_async_session() as session:
			await session.execute(UserSession.__table__.delete().where(UserSession.user_id == current_user.id))
			await session.commit()

		return {'message': 'Successfully logged out'}

	@router.post(
		'/registration',
		status_code=status.HTTP_201_CREATED,
		summary='Регистрация пользователя',
		response_model=str,
	)
	async def api_registration(self, data: Annotated[RegistrationDataForm, Form()]):
		user = User(
			login=data.login,
			email=data.email,
		)
		user.set_password(data.password)
		async with database.get_async_session() as session:
			session.add(user)
			await session.commit()

		return 'ok'
