from sqlalchemy import (
	Boolean,
	CheckConstraint,
	Index,
	SmallInteger,
	String,
	text,
)
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.car.enums import CarDriveType
from apps.vehicles.models.motorcycle.enums import MotorcycleShiftType
from apps.vehicles.models.node.base import VehicleNodeDetailMixin
from apps.vehicles.models.node.vehicle_node import VehicleNode
from apps.vehicles.models.vehicle.enums import VehicleTransmissionType
from apps.vehicles.models.vehicle.vehicle_brand import get_vehicle_brand_link_mixin
from apps.vehicles.models.vehicle.vehicle_concern import get_vehicle_concern_link_mixin
from common.models import IntEnumType
from common.models.fields.enum_types import IntEnumArrayType
from common.models.fields.foreign_key_to import PostgresOnDeleteFK
from common.models.mixins.relations import get_foreign_key_mixin


class TransmissionNodeFieldsMixin:
	"""
	Общие поля коробки передач для узлов-трансмиссий (Car/Motorcycle).

	Чистый mixin без отображения — подмешивается в конкретные JTI-детали
	``CarTransmissionNode`` / ``MotorcycleTransmissionNode``.
	"""

	name: Mapped[str] = mapped_column(String(50), doc='Название')
	index: Mapped[str | None] = mapped_column(String(50), doc='Заводской индекс')
	type: Mapped[VehicleTransmissionType] = mapped_column(
		IntEnumType(VehicleTransmissionType), doc='Тип коробки передач'
	)
	gears: Mapped[int] = mapped_column(SmallInteger, doc='Количество передач')


class CarTransmissionNode(
	VehicleNodeDetailMixin,
	VehicleNode,
	TransmissionNodeFieldsMixin,
	get_vehicle_brand_link_mixin(back_populates='car_transmissions', nullable=True, on_delete='SET NULL'),
	get_vehicle_concern_link_mixin(back_populates='car_transmissions', nullable=True, on_delete='SET NULL'),
):
	"""
	Коробка передач автомобиля как узел (деталь JTI ``VehicleNode``).
	"""

	__mapper_args__ = {'polymorphic_identity': 'car_transmission'}

	drive_types: Mapped[CarDriveType] = mapped_column(
		IntEnumArrayType(CarDriveType),
		default=list,
		doc='Типы привода (массив значений)',
	)
	torque: Mapped[int | None] = mapped_column(
		SmallInteger,
		doc='Максимально допустимый входной момент КПП (Нм)',
	)

	__table_args__ = (
		CheckConstraint(
			'brand_id IS NOT NULL OR concern_id IS NOT NULL',
			name='car_transmission_node_brand_or_concern_required',
		),
		Index(
			'car_transmission_node_brand_type_gears_name_unique',
			'brand_id',
			'type',
			'gears',
			'name',
			unique=True,
			postgresql_where=text('brand_id IS NOT NULL'),
		),
		Index(
			'car_transmission_node_concern_type_gears_name_unique',
			'concern_id',
			'type',
			'gears',
			'name',
			unique=True,
			postgresql_where=text('concern_id IS NOT NULL'),
		),
	)


class MotorcycleTransmissionNode(
	VehicleNodeDetailMixin,
	VehicleNode,
	TransmissionNodeFieldsMixin,
	get_vehicle_brand_link_mixin(back_populates='motorcycle_transmissions', nullable=True, on_delete='SET NULL'),
	get_vehicle_concern_link_mixin(back_populates='motorcycle_transmissions', nullable=True, on_delete='SET NULL'),
):
	"""
	Коробка передач мотоцикла как узел (деталь JTI ``VehicleNode``).
	"""

	__mapper_args__ = {'polymorphic_identity': 'motorcycle_transmission'}

	shift_type: Mapped[MotorcycleShiftType] = mapped_column(
		IntEnumType(MotorcycleShiftType),
		doc='Тип переключения передач',
	)
	slipper_clutch: Mapped[bool] = mapped_column(Boolean, doc='Наличие скользящего сцепления')

	__table_args__ = (
		CheckConstraint(
			'brand_id IS NOT NULL OR concern_id IS NOT NULL',
			name='motorcycle_transmission_node_brand_or_concern_required',
		),
	)


def get_car_transmission_link_mixin(
	back_populates: str | None,
	nullable: bool,
	verbose_name: str = 'Трансмиссия',
	on_delete: PostgresOnDeleteFK = 'CASCADE',
):
	"""
	Миксин связи с КПП-узлом автомобиля (``CarTransmissionNode``).

	Параметр ``on_delete`` обязательно передавать ``'SET NULL'`` для nullable-связей.
	"""
	return get_foreign_key_mixin(
		CarTransmissionNode,
		'transmission',
		back_populates=back_populates,
		nullable=nullable,
		verbose_name=verbose_name,
		on_delete=on_delete,
	)


def get_motorcycle_transmission_link_mixin(
	back_populates: str | None,
	nullable: bool,
	verbose_name: str = 'Трансмиссия',
	on_delete: PostgresOnDeleteFK = 'CASCADE',
):
	"""
	Миксин связи с КПП-узлом мотоцикла (``MotorcycleTransmissionNode``).

	Параметр ``on_delete`` обязательно передавать ``'SET NULL'`` для nullable-связей.
	"""
	return get_foreign_key_mixin(
		MotorcycleTransmissionNode,
		'transmission',
		back_populates=back_populates,
		nullable=nullable,
		verbose_name=verbose_name,
		on_delete=on_delete,
	)
