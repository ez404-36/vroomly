from sqlalchemy import SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from apps.geo.models.country import get_country_link_mixin
from apps.vehicles.models.vehicle.enums import VehicleType
from common.models import IntEnumType
from common.models.mixins.relations import get_foreign_key_mixin
from core.models import AutoSchemaBase


class Vehicle(
    AutoSchemaBase,
    get_country_link_mixin(back_populates='vehicles', nullable=True, verbose_name='Страна производства'),
):
    """
    Общая модель всех ТС.
    Представляет собой объект, существующий в реальном мире.
    """
    vehicle_type: Mapped[VehicleType] = mapped_column(IntEnumType(VehicleType), doc='Тип ТС')
    production_year: Mapped[int] = mapped_column(SmallInteger, doc='Год производства')
    color: Mapped[str | None] = mapped_column(String(100), doc='Цвет (по паспорту)')


def get_vehicle_link_mixin(
    back_populates: str | None,
    nullable: bool,
    verbose_name='ТС',
):
    """
    Миксин связи с общей моделью всех ТС
    """
    return get_foreign_key_mixin(
        Vehicle, 'vehicle',
        back_populates=back_populates, nullable=nullable, verbose_name=verbose_name,
    )
