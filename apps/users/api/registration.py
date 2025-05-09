__all__ = (
    'registration',
)

from typing import Annotated

from fastapi import Form
from pydantic import Field, model_validator, ValidationError

from apps.users.models.user import UserModel
from apps.users.api.routers import router
from config.database import get_async_session
from core.schema import FrozenModelType


class RegistrationData(FrozenModelType):
    login: str = Field(..., min_length=1, max_length=50)
    email: str  # TODO: email validation
    password: str
    confirm_password: str

    @model_validator(mode='after')
    def validate_passwords(self) -> 'RegistrationData':
        if self.password != self.confirm_password:
            raise ValidationError('Passwords do not match')
        return self


@router.post("/registration", status_code=201)
async def registration(data: Annotated[RegistrationData, Form()]):
    user = UserModel(
        login=data.login,
        email=data.email,
    )
    user.set_password(data.password)
    async with get_async_session() as session:
        session.add(user)
