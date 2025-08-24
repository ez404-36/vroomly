from datetime import date

import bcrypt
from sqlalchemy import String, Date
from sqlalchemy.orm import Mapped, mapped_column

from core.settings import settings
from core.models import AutoSchemaBase
from common.models import DeletedModelMixin, TimestampedModelMixin


class User(
    AutoSchemaBase,
    DeletedModelMixin,
    TimestampedModelMixin,
):
    """
    Модель Пользователь
    """

    login: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))

    name: Mapped[str | None]
    surname: Mapped[str | None]
    birth_date: Mapped[date | None] = mapped_column(Date)

    @staticmethod
    def generate_password_hash(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(settings.encoding), salt).decode(settings.encoding)

    def set_password(self, password: str) -> None:
        """Генерация пароля"""
        self.password_hash = self.generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Проверка пароля"""
        return bcrypt.checkpw(password.encode(settings.encoding), self.password_hash.encode(settings.encoding))
