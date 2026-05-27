from apps.vehicles.models.motorcycle.motorcycle_body import get_motorcycle_body_link_mixin
from apps.vehicles.models.motorcycle.motorcycle_transmission import get_motorcycle_transmission_link_mixin
from apps.vehicles.models.vehicle.abstract.vehicle_trim import VehicleTrimAbstract
from apps.vehicles.models.vehicle.vehicle_engine import get_engine_link_mixin
from apps.vehicles.models.vehicle.vehicle_generation import get_vehicle_generation_link_mixin
from common.models.fields.foreign_key_to import PostgresOnDeleteFK
from common.models.mixins.relations import get_foreign_key_mixin


class MotorcycleTrim(
	VehicleTrimAbstract,
	get_engine_link_mixin('motorcycle_trims', False),
	get_vehicle_generation_link_mixin('motorcycle_trims', False),
	get_motorcycle_transmission_link_mixin('motorcycle_trims', False),
	get_motorcycle_body_link_mixin('motorcycle_trims', False),
):
	"""
	Комплектация мотоцикла
	"""


def get_motorcycle_trim_link_mixin(
	back_populates: str | None,
	nullable: bool,
	verbose_name: str = 'Комплектация',
	on_delete: PostgresOnDeleteFK = 'CASCADE',
):
	"""
	Миксин связи с комплектацией мотоцикла.

	Параметр ``on_delete`` обязательно передавать ``'SET NULL'`` для nullable-связей.
	"""
	return get_foreign_key_mixin(
		MotorcycleTrim,
		'trim',
		back_populates=back_populates,
		nullable=nullable,
		verbose_name=verbose_name,
		on_delete=on_delete,
	)
