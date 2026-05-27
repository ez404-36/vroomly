from sqlalchemy import CheckConstraint, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.car.enums import CarDriveType
from apps.vehicles.models.vehicle.abstract.vehicle_transmission import VehicleTransmissionAbstract
from apps.vehicles.models.vehicle.vehicle_brand import get_vehicle_brand_link_mixin
from apps.vehicles.models.vehicle.vehicle_concern import get_vehicle_concern_link_mixin
from common.models.fields.enum_types import IntEnumArrayType
from common.models.fields.foreign_key_to import PostgresOnDeleteFK
from common.models.mixins.relations import get_foreign_key_mixin
from core.models import AutoSchemaBase


class CarTransmission(
    VehicleTransmissionAbstract,
    AutoSchemaBase,
    get_vehicle_brand_link_mixin(back_populates='car_transmissions', nullable=True, on_delete='SET NULL'),
    get_vehicle_concern_link_mixin(back_populates='car_transmissions', nullable=True, on_delete='SET NULL'),
):
    """
    Коробка передач автомобиля
    """

    drive_types: Mapped[CarDriveType] = mapped_column(
        IntEnumArrayType(CarDriveType),
        default=list, doc='Типы привода (массив значений)',
    )
    torque: Mapped[int | None] = mapped_column(
        SmallInteger, doc='Максимально допустимый входной момент КПП (Нм)',
    )

    __table_args__ = (
        CheckConstraint(
            'brand_id IS NOT NULL OR concern_id IS NOT NULL',
            name='car_transmission_brand_or_concern_required',
        ),
    )


def get_car_transmission_link_mixin(
    back_populates: str | None,
    nullable: bool,
    verbose_name: str = 'Трансмиссия',
    on_delete: PostgresOnDeleteFK = 'CASCADE',
):
    """
    Миксин связи с трансмиссией автомобиля.

    Параметр ``on_delete`` обязательно передавать ``'SET NULL'`` для nullable-связей.
    """
    return get_foreign_key_mixin(
        CarTransmission, 'transmission',
        back_populates=back_populates, nullable=nullable,
        verbose_name=verbose_name, on_delete=on_delete,
    )
