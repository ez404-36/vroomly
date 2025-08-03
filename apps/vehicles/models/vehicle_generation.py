from pydantic.v1 import UUID4
from sqlalchemy import String, SmallInteger, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.vehicle_model import VehicleModel
from core.models.base import AutoSchemaBase
from core.models.fields.foreign_key_to import ForeignKeyTo


class VehicleGeneration(AutoSchemaBase):
    """
    Модель "Поколение модели ТС".
    Примеры: E34 (BMW 5), 2 (VW Polo)
    """

    model_id: Mapped[UUID4] = mapped_column(ForeignKeyTo(VehicleModel))
    name: Mapped[str] = mapped_column(String(50))
    is_restyling: Mapped[bool] = mapped_column(Boolean, default=False)
    start_year: Mapped[int] = mapped_column(SmallInteger)
    end_year: Mapped[int | None] = mapped_column(SmallInteger)
