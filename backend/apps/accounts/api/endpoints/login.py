__all__ = (
    "api_get_current_user",
    "api_login",
)

from typing import Annotated

from core.safety.token import Token, create_access_token
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from ..routers import router
from ..schemas.readers import UserDetail
from ..utils import authenticate_user, request_user


@router.get("/me")
async def api_get_current_user(user: UserDetail = request_user) -> UserDetail:
    return user


@router.post("/login")
async def api_login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    token_data = await authenticate_user(form_data.username, form_data.password)

    if not token_data:
        raise HTTPException(status_code=404, detail="User not found")

    access_token = create_access_token(
        data={"sub": token_data.user_id},
    )

    return Token(access_token=access_token, token_type="bearer")
