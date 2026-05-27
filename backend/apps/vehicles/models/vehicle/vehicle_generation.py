from sqlalchemy import Boolean, CheckConstraint, SmallInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.vehicle.vehicle_series import get_vehicle_series_link_mixin
from common.models.mixins.relations import get_foreign_key_mixin
from core.models import AutoSchemaBase

# Та же шкала, что и в Vehicle.production_year.
_GEN_YEAR_MIN = 1885
_GEN_YEAR_MAX = 2100


class VehicleGeneration(
    AutoSchemaBase,
    get_vehicle_series_link_mixin('generations', False),
):
    """
    Поколение модели ТС.
    Примеры: E34 (BMW 5), 2 (VW Polo)
    """

    name: Mapped[str] = mapped_column(String(50), doc='Название поколения')
    is_restyling: Mapped[bool] = mapped_column(Boolean, default=False, doc='Рестайлинг')
    start_year: Mapped[int] = mapped_column(SmallInteger, doc='Начало продаж (год)')
    end_year: Mapped[int | None] = mapped_column(SmallInteger, doc='Окончание продаж (год)')

    __table_args__ = (
        CheckConstraint(
            f'start_year BETWEEN {_GEN_YEAR_MIN} AND {_GEN_YEAR_MAX}',
            name='vehicle_generation_start_year_range',
        ),
        CheckConstraint(
            f'end_year IS NULL OR end_year BETWEEN {_GEN_YEAR_MIN} AND {_GEN_YEAR_MAX}',
            name='vehicle_generation_end_year_range',
        ),
        CheckConstraint(
            'end_year IS NULL OR end_year >= start_year',
            name='vehicle_generation_end_after_start',
        ),
        UniqueConstraint(
            'series_id', 'name', 'is_restyling',
            name='vehicle_generation_series_name_restyling_unique',
        ),
    )


def get_vehicle_generation_link_mixin(
    back_populates: str | None,
    nullable: bool,
    verbose_name='Поколение',
):
    """
    Миксин связи с поколением ТС
    """
    return get_foreign_key_mixin(
        VehicleGeneration, 'generation',
        back_populates=back_populates, nullable=nullable, verbose_name=verbose_name,
    )
