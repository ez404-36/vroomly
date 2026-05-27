from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.vehicle.enums import VehicleType
from apps.vehicles.models.vehicle.vehicle_brand import get_vehicle_brand_link_mixin
from common.models import IntEnumType
from common.models.mixins.relations import get_foreign_key_mixin
from core.models import AutoSchemaBase


class VehicleSeries(
	AutoSchemaBase,
	get_vehicle_brand_link_mixin(back_populates='series', nullable=False),
):
	"""
	Модель марки ТС. Является родительской сущностью для Car, Motorcycle.
	Примеры: Octavia (Skoda), Vesta (Lada)
	"""

	name: Mapped[str] = mapped_column(String(50), doc='Название модели')
	vehicle_type: Mapped[VehicleType] = mapped_column(IntEnumType(VehicleType), doc='Тип ТС')

	__table_args__ = (UniqueConstraint('brand_id', 'name', name='vehicle_series_brand_id_name_unique'),)


def get_vehicle_series_link_mixin(
	back_populates: str | None,
	nullable: bool,
	verbose_name='Модель',
):
	"""Миксин связи с серией (моделью) ТС."""
	return get_foreign_key_mixin(
		VehicleSeries,
		relation_name='series',
		back_populates=back_populates,
		nullable=nullable,
		verbose_name=verbose_name,
	)
