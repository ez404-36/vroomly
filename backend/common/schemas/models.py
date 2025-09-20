from datetime import date

from pydantic import UUID4, BaseModel


class FrozenModelType(BaseModel):
    """
    Модель данных, в которой запрещено изменять поля
    """

    __abstract__ = True

    model_config = {"frozen": True}


class CurrentUser(BaseModel):
    """
    Модель текущего пользователя, доступная в API-запросах
    """

    id: UUID4
    login: str
    email: str
    name: str | None
    surname: str | None
    birth_date: date | None

    class Config:
        from_attributes = True
