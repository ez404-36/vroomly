from decimal import Decimal

from sqlalchemy import Numeric, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.vehicle.abstract.vehicle_trim import VehicleTrimAbstract
from apps.vehicles.models.vehicle.vehicle_generation import get_vehicle_generation_link_mixin
from common.models.mixins.relations import get_foreign_key_mixin


class CarTrim(
    VehicleTrimAbstract,
    get_vehicle_generation_link_mixin('car_trims', False),
):
    """
    Комплектация автомобиля.
    Примеры: Club# (Lada Granta)
    """

    avg_fuel_consumption: Mapped[Decimal | None] = mapped_column(
        Numeric(3, 2, asdecimal=True),
        doc='Средний расход топлива (по паспорту)',
    )
    acceleration: Mapped[Decimal | None] = mapped_column(
        Numeric(3, 2, asdecimal=True),
        doc='Разгон до 100 км/ч (по паспорту)'
    )

    clearance: Mapped[int | None] = mapped_column(SmallInteger, doc='Клиренс')


def get_car_trim_link_mixin(
    back_populates: str | None,
    nullable: bool,
    verbose_name='Комплектация',
):
    """
    Миксин связи с комплектацией автомобиля
    """
    return get_foreign_key_mixin(
        CarTrim, 'trims',
        back_populates=back_populates, nullable=nullable, verbose_name=verbose_name,
    )
