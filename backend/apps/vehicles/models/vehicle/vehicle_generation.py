from sqlalchemy import String, Boolean, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.vehicle.vehicle_series import get_vehicle_series_link_mixin
from common.models.mixins.relations import get_foreign_key_mixin
from core.models import AutoSchemaBase


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
