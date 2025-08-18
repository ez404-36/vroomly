from mako.parsetree import Code
from pydantic.v1 import UUID4
from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from apps.geo.models.country import Country
from core.models.base import AutoSchemaBase
from core.models.fields.foreign_key_to import ForeignKeyTo


class VehicleBrand(AutoSchemaBase):
    """
    Модель "Марка ТС".
    Примеры: Skoda, BMW, Lada
    """

    country_id: Mapped[UUID4] = mapped_column(ForeignKeyTo(Country))
    code: Mapped[str] = mapped_column(String(50))   # КОД_БРЕНДА (англ. язык, верхний регистр)
    name: Mapped[str] = mapped_column(String(50))   # Название бренда на английском языке
    original_name: Mapped[str] = mapped_column(String(50))  # Название бренда на родном языке

    __table_args__ = (
        UniqueConstraint('country_id', 'code', name='vehicle_brand_country_id_code_unique'),
    )
