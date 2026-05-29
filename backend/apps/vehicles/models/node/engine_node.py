from sqlalchemy import CheckConstraint, Index, SmallInteger, String, text
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.node.base import VehicleNodeDetailMixin
from apps.vehicles.models.node.vehicle_node import VehicleNode
from apps.vehicles.models.vehicle.enums import VehicleEngineGRMType, VehicleEngineType
from apps.vehicles.models.vehicle.vehicle_brand import get_vehicle_brand_link_mixin
from apps.vehicles.models.vehicle.vehicle_concern import get_vehicle_concern_link_mixin
from apps.vehicles.models.vehicle.vehicle_engine_phase_regulator_system import get_phase_regulator_system_mixin
from common.models import IntEnumType, IntFlagType
from common.models.fields.foreign_key_to import PostgresOnDeleteFK
from common.models.mixins.relations import get_foreign_key_mixin


class EngineNode(
	VehicleNodeDetailMixin,
	VehicleNode,
	get_vehicle_brand_link_mixin(back_populates='engines', nullable=True, on_delete='SET NULL'),
	get_vehicle_concern_link_mixin(back_populates='engines', nullable=True, on_delete='SET NULL'),
	get_phase_regulator_system_mixin(back_populates='engines', nullable=True, on_delete='SET NULL'),
):
	"""
	Двигатель ТС как узел (деталь JTI ``VehicleNode``).

	Название двигателя, технические характеристики, принадлежность бренду/концерну
	и связь с системой фазорегулирования (явный FK ``phase_regulator_system_id``)
	живут здесь. Базовый ``VehicleNode`` хранит только ``node_type``.
	"""

	__mapper_args__ = {'polymorphic_identity': 'engine'}

	name: Mapped[str] = mapped_column(String(50), doc='Название двигателя')
	volume: Mapped[int] = mapped_column(SmallInteger, doc='Рабочий объём (сс)')
	power: Mapped[int] = mapped_column(SmallInteger, doc='Мощность (л.с)')
	type: Mapped[VehicleEngineType] = mapped_column(IntFlagType(VehicleEngineType), doc='Тип двигателя')
	eco_class: Mapped[str | None] = mapped_column(String(50), doc='Экологический класс')
	cylinders: Mapped[int | None] = mapped_column(SmallInteger, doc='Кол-во цилиндров')
	valves: Mapped[int | None] = mapped_column(SmallInteger, doc='Кол-во клапанов')
	torque: Mapped[int | None] = mapped_column(SmallInteger, doc='Крутящий момент двигателя (Нм)')
	grm_drive_type: Mapped[VehicleEngineGRMType] = mapped_column(
		IntEnumType(VehicleEngineGRMType),
		doc='Тип привода ГРМ',
	)

	__table_args__ = (
		CheckConstraint(
			'brand_id IS NOT NULL OR concern_id IS NOT NULL',
			name='engine_node_brand_or_concern_required',
		),
		Index(
			'engine_node_brand_name_volume_power_unique',
			'brand_id',
			'name',
			'volume',
			'power',
			unique=True,
			postgresql_where=text('brand_id IS NOT NULL'),
		),
		Index(
			'engine_node_concern_name_volume_power_unique',
			'concern_id',
			'name',
			'volume',
			'power',
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
	Миксин связи с двигателем-узлом (``EngineNode``).

	Параметр ``on_delete`` обязательно передавать ``'SET NULL'`` для nullable-связей.
	"""
	return get_foreign_key_mixin(
		EngineNode,
		'engine',
		back_populates=back_populates,
		nullable=nullable,
		verbose_name=verbose_name,
		on_delete=on_delete,
	)
