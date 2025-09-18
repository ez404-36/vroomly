__all__ = ("api_registration",)

from typing import Annotated

from apps.accounts.api.routers import router
from apps.accounts.api.schemas.mutators import RegistrationData
from apps.accounts.models.user import User
from core.db import database
from fastapi import Form


@router.post("/registration", status_code=201)
async def api_registration(data: Annotated[RegistrationData, Form()]):
    user = User(
        login=data.login,
        email=data.email,
    )
    user.set_password(data.password)
    async with database.get_async_session() as session:
        session.add(user)
        await session.commit()
