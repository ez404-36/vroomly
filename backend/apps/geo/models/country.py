from core.models import AutoSchemaBase
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class Country(AutoSchemaBase):
    """
    Модель "Страна"
    """

    id: Mapped[str] = mapped_column(String(3), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    short_name: Mapped[str | None] = mapped_column(
        String(20), unique=True, nullable=True
    )
