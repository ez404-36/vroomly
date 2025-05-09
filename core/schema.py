from pydantic import BaseModel


class FrozenModelType(BaseModel):
    """
    Модель данных, в которой запрещено изменять поля
    """

    __abstract__ = True

    model_config = {"frozen": True}
