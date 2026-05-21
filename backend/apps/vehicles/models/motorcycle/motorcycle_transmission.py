from sqlalchemy import Boolean
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.motorcycle.enums import MotorcycleShiftType
from apps.vehicles.models.vehicle.abstract.vehicle_transmission import VehicleTransmissionAbstract
from apps.vehicles.models.vehicle.vehicle_brand import get_vehicle_brand_link_mixin
from apps.vehicles.models.vehicle.vehicle_concern import get_vehicle_concern_link_mixin
from common.models import IntEnumType
from common.models.mixins.relations import get_foreign_key_mixin
from core.models import AutoSchemaBase


class MotorcycleTransmission(
    VehicleTransmissionAbstract,
    AutoSchemaBase,
    get_vehicle_brand_link_mixin(back_populates='motorcycle_transmissions', nullable=True),
    get_vehicle_concern_link_mixin(back_populates='motorcycle_transmissions', nullable=True),
):
    """
    Коробка переда мотоцикла
    """

    shift_type: Mapped[MotorcycleShiftType] = mapped_column(
        IntEnumType(MotorcycleShiftType),
        doc='Тип переключения передач',
    )
    slipper_clutch: Mapped[bool] = mapped_column(Boolean, doc='Наличие скользящего сцепления')


def get_motorcycle_transmission_link_mixin(
    back_populates: str | None,
    nullable: bool,
    verbose_name='Трансмиссия',
):
    """
    Миксин связи с трансмиссией мотоцикла
    """
    return get_foreign_key_mixin(
        MotorcycleTransmission, 'transmission',
        back_populates=back_populates, nullable=nullable, verbose_name=verbose_name,
    )
