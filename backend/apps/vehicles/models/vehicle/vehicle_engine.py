from sqlalchemy import CheckConstraint, Index, SmallInteger, String, text
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.vehicle.enums import VehicleEngineGRMType, VehicleEnginePhaseRegulatorType, VehicleEngineType
from apps.vehicles.models.vehicle.vehicle_brand import get_vehicle_brand_link_mixin
from apps.vehicles.models.vehicle.vehicle_concern import get_vehicle_concern_link_mixin
from apps.vehicles.models.vehicle.vehicle_engine_phase_regulator_system import get_phase_regulator_system_mixin
from common.models import IntEnumType, IntFlagType
from common.models.fields.foreign_key_to import PostgresOnDeleteFK
from common.models.mixins.relations import get_foreign_key_mixin
from core.models import AutoSchemaBase


class VehicleEngine(
    AutoSchemaBase,
    get_vehicle_brand_link_mixin(back_populates='engines', nullable=True, on_delete='SET NULL'),
    get_vehicle_concern_link_mixin(back_populates='engines', nullable=True, on_delete='SET NULL'),
    get_phase_regulator_system_mixin(back_populates='engines', nullable=True, on_delete='SET NULL'),
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
    torque: Mapped[int | None] = mapped_column(SmallInteger, doc='Крутящий момент двигателя (Нм)')
    # TODO: Привод может быть цепь + ремень, 2 ремня, 2 ремня + цепь, 2 цепи у ремень.
    #  Надо наверно добавить отдельно поля с кол-вом ремней и отдельно с кол-вом цепей
    grm_drive_type: Mapped[VehicleEngineGRMType] = mapped_column(
        IntEnumType(VehicleEngineGRMType), doc='Тип привода ГРМ',
    )
    phase_regulator_type: Mapped[VehicleEnginePhaseRegulatorType | None] = mapped_column(
        IntEnumType(VehicleEnginePhaseRegulatorType), doc='Фазорегулятор'
    )

    __table_args__ = (
        CheckConstraint(
            'brand_id IS NOT NULL OR concern_id IS NOT NULL',
            name='vehicle_engine_brand_or_concern_required',
        ),
        Index(
            'vehicle_engine_brand_name_volume_power_unique',
            'brand_id', 'name', 'volume', 'power',
            unique=True,
            postgresql_where=text('brand_id IS NOT NULL'),
        ),
        Index(
            'vehicle_engine_concern_name_volume_power_unique',
            'concern_id', 'name', 'volume', 'power',
            unique=True,
            postgresql_where=text('concern_id IS NOT NULL'),
        ),
    )


def get_engine_link_mixin(
    back_populates: str | None,
    nullable: bool,
    verbose_name: str = 'Двигатель',
    on_delete: PostgresOnDeleteFK = 'CASCADE',
):
    """
    Миксин связи с двигателем ТС.

    Параметр ``on_delete`` обязательно передавать ``'SET NULL'`` для nullable-связей.
    """
    return get_foreign_key_mixin(
        VehicleEngine, 'engine',
        back_populates=back_populates, nullable=nullable,
        verbose_name=verbose_name, on_delete=on_delete,
    )
