from sqlalchemy import SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.vehicle.enums import VehicleEngineType
from common.models import IntFlagType
from common.models.mixins.relations import get_foreign_key_mixin
from core.models import AutoSchemaBase


class VehicleEngine(
    AutoSchemaBase,
):
    """
    Модель "Двигатель ТС"
    """

    name: Mapped[str] = mapped_column(String(50), doc='Название двигателя')
    displacement: Mapped[int] = mapped_column(SmallInteger, doc='Рабочий объём (сс)')
    power: Mapped[int] = mapped_column(SmallInteger, doc='Мощность (л.с)')
    type: Mapped[VehicleEngineType] = mapped_column(IntFlagType(VehicleEngineType), doc='Тип двигателя')


def get_engine_link_mixin(
    back_populates: str | None,
    nullable: bool,
    verbose_name='Двигатель',
):
    """
    Миксин связи с двигателем ТС
    """
    return get_foreign_key_mixin(
        VehicleEngine, 'engine',
        back_populates=back_populates, nullable=nullable, verbose_name=verbose_name,
    )
