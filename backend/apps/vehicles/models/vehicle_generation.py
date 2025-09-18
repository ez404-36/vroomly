from apps.vehicles.models.vehicle_model import VehicleModel
from common.models import ForeignKeyTo
from core.models import AutoSchemaBase
from pydantic.v1 import UUID4
from sqlalchemy import Boolean, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column


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
