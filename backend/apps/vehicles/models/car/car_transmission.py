from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.car.enums import CarDriveType
from apps.vehicles.models.vehicle.abstract.vehicle_transmission import VehicleTransmissionAbstract
from common.models import IntEnumType
from core.models import AutoSchemaBase


class CarTransmission(
    VehicleTransmissionAbstract,
    AutoSchemaBase,
):
    """
    Коробка передач автомобиля
    """

    drive_type: Mapped[CarDriveType] = mapped_column(IntEnumType(CarDriveType), doc='Тип привода')
