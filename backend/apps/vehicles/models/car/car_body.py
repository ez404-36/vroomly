from sqlalchemy import SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.car.enums import CarBodyType
from apps.vehicles.models.vehicle.abstract.vehicle_body import VehicleBodyAbstract
from common.models import IntEnumType
from common.models.mixins.relations import get_foreign_key_mixin
from core.models import AutoSchemaBase


class CarBody(
    VehicleBodyAbstract,
    AutoSchemaBase,
):
    """
    Кузов автомобиля
    """

    type: Mapped[CarBodyType] = mapped_column(
        IntEnumType(CarBodyType), doc='Тип кузова'
    )
    trunk_volume: Mapped[int | None] = mapped_column(SmallInteger, doc='Объем багажника')


def get_car_body_link_mixin(
    back_populates: str | None,
    nullable: bool,
    verbose_name='Кузов',
):
    """
    Миксин связи с кузовом автомобиля
    """
    return get_foreign_key_mixin(
        CarBody, 'body',
        back_populates=back_populates, nullable=nullable, verbose_name=verbose_name,
    )
