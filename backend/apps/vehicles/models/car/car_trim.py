from decimal import Decimal

from sqlalchemy import Numeric, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.node.body_node import get_car_body_link_mixin
from apps.vehicles.models.node.engine_node import get_engine_link_mixin
from apps.vehicles.models.node.transmission_node import get_car_transmission_link_mixin
from apps.vehicles.models.vehicle.abstract.vehicle_trim import VehicleTrimAbstract
from apps.vehicles.models.vehicle.vehicle_generation import get_vehicle_generation_link_mixin
from common.models.fields.foreign_key_to import PostgresOnDeleteFK
from common.models.mixins.relations import get_foreign_key_mixin


class CarTrim(
	VehicleTrimAbstract,
	get_engine_link_mixin('car_trims', False),
	get_vehicle_generation_link_mixin('car_trims', False),
	get_car_transmission_link_mixin('car_trims', False),
	get_car_body_link_mixin('car_trims', True, on_delete='SET NULL'),
):
	"""
	Комплектация автомобиля.
	Примеры: Club# (Lada Granta).

	``drive_type`` (тип привода) живёт на ``CarTransmission.drive_types``
	как массив — источник истины. Получить привод комплектации можно через
	``trim.transmission.drive_types``.

	Кузов нормализуется через сущность ``CarBody`` (см. ``body_id``).
	Поскольку справочник кузовов ещё не наполнен, ``body_id`` сделан
	nullable, а исходное текстовое обозначение кузова из импорта (например,
	``E210``, ``Type 939``) сохраняется в ``body_str``. Когда ``car_body``
	будет наполнен, ``body_str`` следует перевести в ``body_id`` и удалить.
	"""

	avg_fuel_consumption: Mapped[Decimal | None] = mapped_column(
		Numeric(4, 2, asdecimal=True),
		doc='Средний расход топлива (по паспорту)',
	)
	acceleration: Mapped[Decimal | None] = mapped_column(
		Numeric(4, 2, asdecimal=True), doc='Разгон до 100 км/ч (по паспорту)'
	)
	clearance: Mapped[int | None] = mapped_column(SmallInteger, doc='Клиренс')
	body_str: Mapped[str | None] = mapped_column(
		String(50),
		doc=(
			'Текстовое обозначение кузова из источника импорта (например, E210, '
			'Type 939). Временное поле до наполнения справочника CarBody.'
		),
	)


def get_car_trim_link_mixin(
	back_populates: str | None,
	nullable: bool,
	verbose_name: str = 'Комплектация',
	on_delete: PostgresOnDeleteFK = 'CASCADE',
):
	"""
	Миксин связи с комплектацией автомобиля.

	Параметр ``on_delete`` обязательно передавать ``'SET NULL'`` для nullable-связей.
	"""
	return get_foreign_key_mixin(
		CarTrim,
		'trim',
		back_populates=back_populates,
		nullable=nullable,
		verbose_name=verbose_name,
		on_delete=on_delete,
	)
