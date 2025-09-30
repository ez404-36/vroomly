from sqlalchemy import SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.vehicle.enums import VehicleTransmissionType
from common.models import IntEnumType
from core.models import AutoSchemaBase


class VehicleTransmissionAbstract(
    AutoSchemaBase,
):
    """
    Базовый класс коробки передач
    """
    __abstract__ = True

    type: Mapped[VehicleTransmissionType] = mapped_column(
        IntEnumType(VehicleTransmissionType), doc='Тип коробки передач'
    )
    gears: Mapped[int] = mapped_column(SmallInteger, doc='Количество передач')
