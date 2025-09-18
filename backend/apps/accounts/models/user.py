from datetime import date

import bcrypt
from common.models import DeletedModelMixin, TimestampedModelMixin
from core.models import AutoSchemaBase
from core.settings import settings
from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column


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
        return bcrypt.hashpw(password.encode(settings.encoding), salt).decode(
            settings.encoding
        )

    def set_password(self, password: str) -> None:
        """Генерация пароля"""
        self.password_hash = self.generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Проверка пароля"""
        return bcrypt.checkpw(
            password.encode(settings.encoding),
            self.password_hash.encode(settings.encoding),
        )
