from sqlalchemy import String, SmallInteger
from sqlalchemy.orm import mapped_column, Mapped

from apps.vehicles.models.enums import EngineType
from core.models import AutoSchemaBase
from common.models import IntFlagType


class VehicleEngine(
    AutoSchemaBase,
):
    """
    Модель "Двигатель ТС"
    """

    name: Mapped[str] = mapped_column(String(50))
    power: Mapped[int] = mapped_column(SmallInteger)
    type: Mapped[EngineType] = mapped_column(IntFlagType(EngineType))
