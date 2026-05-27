from sqlalchemy import Boolean, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.motorcycle.enums import MotorcycleShiftType
from apps.vehicles.models.vehicle.abstract.vehicle_transmission import VehicleTransmissionAbstract
from apps.vehicles.models.vehicle.vehicle_brand import get_vehicle_brand_link_mixin
from apps.vehicles.models.vehicle.vehicle_concern import get_vehicle_concern_link_mixin
from common.models import IntEnumType
from common.models.fields.foreign_key_to import PostgresOnDeleteFK
from common.models.mixins.relations import get_foreign_key_mixin
from core.models import AutoSchemaBase


class MotorcycleTransmission(
    VehicleTransmissionAbstract,
    AutoSchemaBase,
    get_vehicle_brand_link_mixin(back_populates='motorcycle_transmissions', nullable=True, on_delete='SET NULL'),
    get_vehicle_concern_link_mixin(back_populates='motorcycle_transmissions', nullable=True, on_delete='SET NULL'),
):
    """
    Коробка переда мотоцикла
    """

    shift_type: Mapped[MotorcycleShiftType] = mapped_column(
        IntEnumType(MotorcycleShiftType),
        doc='Тип переключения передач',
    )
    slipper_clutch: Mapped[bool] = mapped_column(Boolean, doc='Наличие скользящего сцепления')

    __table_args__ = (
        CheckConstraint(
            'brand_id IS NOT NULL OR concern_id IS NOT NULL',
            name='motorcycle_transmission_brand_or_concern_required',
        ),
    )


def get_motorcycle_transmission_link_mixin(
    back_populates: str | None,
    nullable: bool,
    verbose_name: str = 'Трансмиссия',
    on_delete: PostgresOnDeleteFK = 'CASCADE',
):
    """
    Миксин связи с трансмиссией мотоцикла.

    Параметр ``on_delete`` обязательно передавать ``'SET NULL'`` для nullable-связей.
    """
    return get_foreign_key_mixin(
        MotorcycleTransmission, 'transmission',
        back_populates=back_populates, nullable=nullable,
        verbose_name=verbose_name, on_delete=on_delete,
    )
