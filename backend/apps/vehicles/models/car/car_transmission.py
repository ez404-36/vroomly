from sqlalchemy import SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.car.enums import CarDriveType
from apps.vehicles.models.vehicle.abstract.vehicle_transmission import VehicleTransmissionAbstract
from common.models import IntEnumType
from common.models.mixins.relations import get_foreign_key_mixin
from core.models import AutoSchemaBase


class CarTransmission(
    VehicleTransmissionAbstract,
    AutoSchemaBase,
):
    """
    Коробка передач автомобиля
    """

    drive_type: Mapped[CarDriveType] = mapped_column(
        IntEnumType(CarDriveType), doc='Тип привода',
    )
    torque: Mapped[int | None] = mapped_column(
        SmallInteger, doc='Крутящий момент (Нм)',
    )


def get_car_transmission_link_mixin(
    back_populates: str | None,
    nullable: bool,
    verbose_name='Трансмиссия',
):
    """
    Миксин связи с трансмиссией автомобиля
    """
    return get_foreign_key_mixin(
        CarTransmission, 'transmission',
        back_populates=back_populates, nullable=nullable, verbose_name=verbose_name,
    )
