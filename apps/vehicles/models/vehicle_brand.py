from pydantic.v1 import UUID4
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from apps.geo.models.country import Country
from core.models.base import AutoSchemaBase
from core.models.fields.foreign_key_to import ForeignKeyTo


class VehicleBrand(AutoSchemaBase):
    """
    Модель "Марка ТС".
    Примеры: Skoda, BMW, Lada
    """

    # TODO: уникальность надо поддерживать по полям country_id + name
    country_id: Mapped[UUID4] = mapped_column(ForeignKeyTo(Country))
    name: Mapped[str] = mapped_column(String(50), unique=True)
