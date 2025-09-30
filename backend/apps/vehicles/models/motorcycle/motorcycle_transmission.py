from sqlalchemy import Boolean
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.motorcycle.enums import MotorcycleShiftType
from apps.vehicles.models.vehicle.abstract.vehicle_transmission import VehicleTransmissionAbstract
from common.models import IntEnumType
from core.models import AutoSchemaBase


class MotorcycleTransmission(
    VehicleTransmissionAbstract,
    AutoSchemaBase,
):
    """
    Коробка переда мотоцикла
    """

    shift_type: Mapped[MotorcycleShiftType] = mapped_column(IntEnumType(MotorcycleShiftType), doc='Тип переключения передач')
    slipper_clutch: Mapped[bool] = mapped_column(Boolean, doc='Наличие скользящего сцепления')
