from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import AutoSchemaBase


class Country(AutoSchemaBase):
    """
    Модель "Страна"
    """
    name: Mapped[str] = mapped_column(String(20), unique=True)
    full_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=True)
