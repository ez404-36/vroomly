from apps.vehicles.models.enums import EngineType
from common.models import IntFlagType
from core.models import AutoSchemaBase
from sqlalchemy import SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column


class VehicleEngine(
    AutoSchemaBase,
):
    """
    Модель "Двигатель ТС"
    """

    name: Mapped[str] = mapped_column(String(50))
    power: Mapped[int] = mapped_column(SmallInteger)
    type: Mapped[EngineType] = mapped_column(IntFlagType(EngineType))
