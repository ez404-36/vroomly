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
    name: Mapped[str] = mapped_column(String(50))

    __table_args__ = (
        UniqueConstraint('country_id', 'name', name='vehicle_brand_country_id_name_unique'),
    )
