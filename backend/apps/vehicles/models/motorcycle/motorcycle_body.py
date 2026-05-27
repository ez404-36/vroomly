from sqlalchemy import SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.motorcycle.enums import MotorcycleBodyType
from apps.vehicles.models.vehicle.abstract.vehicle_body import VehicleBodyAbstract
from common.models import IntEnumType
from common.models.mixins.relations import get_foreign_key_mixin
from core.models import AutoSchemaBase


class MotorcycleBody(
	VehicleBodyAbstract,
	AutoSchemaBase,
):
	"""
	Спецификация кузова мотоцикла
	"""

	type: Mapped[MotorcycleBodyType] = mapped_column(IntEnumType(MotorcycleBodyType), doc='Тип кузова')
	seat_height: Mapped[int | None] = mapped_column(SmallInteger, doc='Высота сиденья')


def get_motorcycle_body_link_mixin(
	back_populates: str | None,
	nullable: bool,
	verbose_name='Кузов',
):
	"""
	Миксин связи с кузовом мотоцикла
	"""
	return get_foreign_key_mixin(
		MotorcycleBody,
		'body',
		back_populates=back_populates,
		nullable=nullable,
		verbose_name=verbose_name,
	)
