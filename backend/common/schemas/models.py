from datetime import date

from uuid import UUID

from fastapi_utils.api_model import APIModel
from pydantic import BaseModel


class FrozenModelType(BaseModel):
    """
    Модель данных, в которой запрещено изменять поля
    """

    __abstract__ = True

    model_config = {"frozen": True}


class CurrentUser(APIModel):
    """
    Модель текущего пользователя, доступная в API-запросах
    """

    id: UUID
    login: str
    email: str
    name: str | None
    surname: str | None
    birth_date: date | None
