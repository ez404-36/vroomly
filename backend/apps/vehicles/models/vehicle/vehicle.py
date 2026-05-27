from sqlalchemy import Boolean, CheckConstraint, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from apps.geo.models.country import get_country_link_mixin
from apps.vehicles.models.vehicle.enums import VehicleType
from common.models import IntEnumType
from common.models.mixins.relations import get_foreign_key_mixin
from core.models import AutoSchemaBase

# Год выпуска первого автомобиля (Benz Patent-Motorwagen, 1885) — нижняя граница.
# Верхняя — 2100 (с большим запасом, чтобы CHECK не пришлось обновлять).
_VEHICLE_YEAR_MIN = 1885
_VEHICLE_YEAR_MAX = 2100


class Vehicle(
    AutoSchemaBase,
    get_country_link_mixin(
        back_populates='vehicles', nullable=True,
        verbose_name='Страна производства', on_delete='SET NULL',
    ),
):
    """
    Общая модель всех ТС.
    Представляет собой объект, существующий в реальном мире.

    Пробег и единицы измерения — атрибуты экземпляра, не зависят от
    владельца. При смене владельца пробег сохраняется.
    """
    vehicle_type: Mapped[VehicleType] = mapped_column(IntEnumType(VehicleType), doc='Тип ТС')
    production_year: Mapped[int] = mapped_column(SmallInteger, doc='Год производства')
    color: Mapped[str | None] = mapped_column(String(100), nullable=True, doc='Цвет (по паспорту)')
    mileage: Mapped[int | None] = mapped_column(
        Integer, doc='Пробег',
    )
    is_mileage_in_miles: Mapped[bool] = mapped_column(
        Boolean, default=False, doc='Пробег измеряется в милях ?',
    )

    __table_args__ = (
        CheckConstraint(
            f'production_year BETWEEN {_VEHICLE_YEAR_MIN} AND {_VEHICLE_YEAR_MAX}',
            name='vehicle_production_year_range',
        ),
        CheckConstraint(
            'mileage IS NULL OR mileage >= 0',
            name='vehicle_mileage_non_negative',
        ),
    )


def get_vehicle_link_mixin(
    back_populates: str | None,
    nullable: bool,
    verbose_name: str = 'ТС',
    back_uselist: bool = True,
):
    """
    Миксин связи с общей моделью всех ТС.

    Параметр ``back_uselist=False`` нужен для 1:1-связи Vehicle ↔ Spec:
    на стороне Vehicle обратная коллекция будет скалярным атрибутом.
    """
    return get_foreign_key_mixin(
        Vehicle, 'vehicle',
        back_populates=back_populates, nullable=nullable,
        verbose_name=verbose_name, back_uselist=back_uselist,
    )
