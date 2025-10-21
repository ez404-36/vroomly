from sqlalchemy import Boolean, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.vehicle.enums import VehicleEngineGRMType, VehicleEngineType
from common.models import IntEnumType, IntFlagType
from common.models.mixins.relations import get_foreign_key_mixin
from core.models import AutoSchemaBase


class VehicleEngine(
    AutoSchemaBase,
):
    """
    Модель "Двигатель ТС"
    """

    name: Mapped[str] = mapped_column(String(50), doc='Название двигателя')
    volume: Mapped[int] = mapped_column(SmallInteger, doc='Рабочий объём (сс)')
    power: Mapped[int] = mapped_column(SmallInteger, doc='Мощность (л.с)')
    type: Mapped[VehicleEngineType] = mapped_column(IntFlagType(VehicleEngineType), doc='Тип двигателя')
    eco_class: Mapped[str | None] = mapped_column(String(50), doc='Экологический класс')
    cylinders: Mapped[int | None] = mapped_column(SmallInteger, doc='Кол-во цилиндров')
    valves: Mapped[int | None] = mapped_column(SmallInteger, doc='Кол-во клапанов')
    torque: Mapped[int | None] = mapped_column(SmallInteger, doc='Крутящий момент (Нм)')
    grm_drive_type: Mapped[VehicleEngineGRMType] = mapped_column(
        IntEnumType(VehicleEngineGRMType), doc='Тип привода ГРМ',
    )
    phase_regulator: Mapped[bool | None] = mapped_column(Boolean, doc='Фазорегулятор')


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
