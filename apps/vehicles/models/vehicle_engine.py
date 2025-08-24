from enum import IntFlag

from sqlalchemy import String, SmallInteger
from sqlalchemy.orm import mapped_column, Mapped

from core.models import AutoSchemaBase
from common.models import IntFlagType


class EngineType(IntFlag):
    PETROL = 0
    DIESEL = 1
    ELECTRO = 2
    GAS = 4
    ATMOSPHERIC = 8
    TURBO = 16


class VehicleEngine(
    AutoSchemaBase,
):
    """
    Модель "Двигатель ТС"
    """

    name: Mapped[str] = mapped_column(String(50))
    power: Mapped[int] = mapped_column(SmallInteger)
    type: Mapped[EngineType] = mapped_column(IntFlagType(EngineType))
