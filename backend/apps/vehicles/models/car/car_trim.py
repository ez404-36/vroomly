from decimal import Decimal

from sqlalchemy import Numeric, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.car.car_body import get_car_body_link_mixin
from apps.vehicles.models.car.car_transmission import get_car_transmission_link_mixin
from apps.vehicles.models.vehicle.abstract.vehicle_trim import VehicleTrimAbstract
from apps.vehicles.models.vehicle.vehicle_engine import get_engine_link_mixin
from apps.vehicles.models.vehicle.vehicle_generation import get_vehicle_generation_link_mixin
from common.models.fields.foreign_key_to import PostgresOnDeleteFK
from common.models.mixins.relations import get_foreign_key_mixin


class CarTrim(
    VehicleTrimAbstract,
    get_engine_link_mixin('car_trims', False),
    get_vehicle_generation_link_mixin('car_trims', False),
    get_car_transmission_link_mixin('car_trims', False),
    get_car_body_link_mixin('car_trims', False),
):
    """
    Комплектация автомобиля.
    Примеры: Club# (Lada Granta).

    ``drive_type`` (тип привода) живёт на ``CarTransmission.drive_types``
    как массив — источник истины. Получить привод комплектации можно через
    ``trim.transmission.drive_types``.

    Кузов всегда нормализованная сущность ``CarBody`` (см. ``body_id``).
    Раньше тут было поле ``body_str`` как временное текстовое представление —
    оно удалено в шаге 5 рефакторинга (см. GRAPH.md).
    """

    avg_fuel_consumption: Mapped[Decimal | None] = mapped_column(
        Numeric(4, 2, asdecimal=True),
        doc='Средний расход топлива (по паспорту)',
    )
    acceleration: Mapped[Decimal | None] = mapped_column(
        Numeric(4, 2, asdecimal=True),
        doc='Разгон до 100 км/ч (по паспорту)'
    )
    clearance: Mapped[int | None] = mapped_column(SmallInteger, doc='Клиренс')


def get_car_trim_link_mixin(
    back_populates: str | None,
    nullable: bool,
    verbose_name: str = 'Комплектация',
    on_delete: PostgresOnDeleteFK = 'CASCADE',
):
    """
    Миксин связи с комплектацией автомобиля.

    Параметр ``on_delete`` обязательно передавать ``'SET NULL'`` для nullable-связей.
    """
    return get_foreign_key_mixin(
        CarTrim, 'trim',
        back_populates=back_populates, nullable=nullable,
        verbose_name=verbose_name, on_delete=on_delete,
    )
