from typing import Annotated

from fastapi import Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_utils.cbv import cbv
from starlette import status

from apps.accounts.api.routers import router
from apps.accounts.api.schemas.mutators import RegistrationDataForm
from apps.accounts.api.utils import authenticate_user
from apps.accounts.models.user import User
from core.db import database
from core.safety.token import create_access_token, Token


@cbv(router)
class UserAuthAPI:
    @router.post(
        "/login",
        summary="Аутентификация пользователя",
    )
    async def api_login(self, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
        token_data = await authenticate_user(form_data.username, form_data.password)

        if not token_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        access_token = create_access_token(
            data={"sub": token_data.user_id},
        )

        return Token(access_token=access_token, token_type="bearer")

    @router.post(
        "/registration",
        status_code=status.HTTP_201_CREATED,
        summary="Регистрация пользователя",
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
