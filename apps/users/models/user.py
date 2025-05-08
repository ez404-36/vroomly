from datetime import date

import bcrypt
from sqlalchemy import String, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.settings import settings
from core.models.base import BaseModel
from core.models.mixins.deleted import DeletedModelMixin
from core.models.mixins.timestamped_model import TimestampedModelMixin


class UserModel(
    BaseModel,
    DeletedModelMixin,
    TimestampedModelMixin,
):
    """
    Модель пользователя
    """

    login: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))

    name: Mapped[str | None]
    surname: Mapped[str | None]
    birth_date: Mapped[date] = mapped_column(Date, unique=True)

    workspaces: Mapped[list['WorkspaceModel']] = relationship(
        'WorkspaceModel',
        back_populates='user',
    )

    def set_password(self, password: str) -> None:
        """Генерация пароля"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode(settings.ENCODING), salt).decode(settings.ENCODING)

    def check_password(self, password: str) -> bool:
        """Проверка пароля"""
        return bcrypt.checkpw(password.encode(settings.ENCODING), self.password_hash.encode(settings.ENCODING))
