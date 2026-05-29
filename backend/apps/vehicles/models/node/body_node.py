from sqlalchemy import SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.car.enums import CarBodyType
from apps.vehicles.models.motorcycle.enums import MotorcycleBodyType
from apps.vehicles.models.node.base import VehicleNodeDetailMixin
from apps.vehicles.models.node.vehicle_node import VehicleNode
from apps.vehicles.models.vehicle.enums import VehicleBodyType
from common.models import IntEnumType, IntFlagType
from common.models.fields.foreign_key_to import PostgresOnDeleteFK
from common.models.mixins.relations import get_foreign_key_mixin


class BodyNodeFieldsMixin:
	"""
	Общие поля кузова для узлов-кузовов (Car/Motorcycle).

	Чистый mixin без отображения — подмешивается в конкретные JTI-детали
	``CarBodyNode`` / ``MotorcycleBodyNode``.
	"""

	name: Mapped[str | None] = mapped_column(String(50), doc='Название кузова')
	material: Mapped[VehicleBodyType | None] = mapped_column(
		IntFlagType(VehicleBodyType),
		doc='Основной материал кузова (комбинация флагов VehicleBodyType)',
	)


class CarBodyNode(
	VehicleNodeDetailMixin,
	VehicleNode,
	BodyNodeFieldsMixin,
):
	"""
	Кузов автомобиля как узел (деталь JTI ``VehicleNode``).
	"""

	__mapper_args__ = {'polymorphic_identity': 'car_body'}

	type: Mapped[CarBodyType] = mapped_column(IntEnumType(CarBodyType), doc='Тип кузова')
	trunk_volume: Mapped[int | None] = mapped_column(SmallInteger, doc='Объем багажника')


class MotorcycleBodyNode(
	VehicleNodeDetailMixin,
	VehicleNode,
	BodyNodeFieldsMixin,
):
	"""
	Кузов мотоцикла как узел (деталь JTI ``VehicleNode``).
	"""

	__mapper_args__ = {'polymorphic_identity': 'motorcycle_body'}

	type: Mapped[MotorcycleBodyType] = mapped_column(IntEnumType(MotorcycleBodyType), doc='Тип кузова')
	seat_height: Mapped[int | None] = mapped_column(SmallInteger, doc='Высота сиденья')


def get_car_body_link_mixin(
	back_populates: str | None,
	nullable: bool,
	verbose_name: str = 'Кузов',
	on_delete: PostgresOnDeleteFK = 'CASCADE',
):
	"""
	Миксин связи с кузовом-узлом автомобиля (``CarBodyNode``).

	Параметр ``on_delete`` обязательно передавать ``'SET NULL'`` для nullable-связей.
	"""
	return get_foreign_key_mixin(
		CarBodyNode,
		'body',
		back_populates=back_populates,
		nullable=nullable,
		verbose_name=verbose_name,
		on_delete=on_delete,
	)


def get_motorcycle_body_link_mixin(
	back_populates: str | None,
	nullable: bool,
	verbose_name: str = 'Кузов',
	on_delete: PostgresOnDeleteFK = 'CASCADE',
):
	"""
	Миксин связи с кузовом-узлом мотоцикла (``MotorcycleBodyNode``).

	Параметр ``on_delete`` обязательно передавать ``'SET NULL'`` для nullable-связей.
	"""
	return get_foreign_key_mixin(
		MotorcycleBodyNode,
		'body',
		back_populates=back_populates,
		nullable=nullable,
		verbose_name=verbose_name,
		on_delete=on_delete,
	)
