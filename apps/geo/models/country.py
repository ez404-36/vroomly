from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import AutoSchemaBase


class Country(AutoSchemaBase):
    """
    Модель "Страна"
    """
    prefix: Mapped[str] = mapped_column(String(3), unique=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    short_name: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
