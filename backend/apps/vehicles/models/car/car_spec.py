from typing import TYPE_CHECKING

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.car.car_transmission import get_car_transmission_link_mixin
from apps.vehicles.models.car.car_trim import get_car_trim_link_mixin
from apps.vehicles.models.utils import SpecBackRefs
from apps.vehicles.models.vehicle.vehicle import get_vehicle_link_mixin
from apps.vehicles.models.vehicle.vehicle_engine import get_engine_link_mixin
from core.models import AutoSchemaBase

if TYPE_CHECKING:
	from apps.vehicles.models.car.car_transmission import CarTransmission
	from apps.vehicles.models.vehicle.vehicle_engine import VehicleEngine


class CarSpec(
	AutoSchemaBase,
	get_vehicle_link_mixin(SpecBackRefs.CAR, nullable=False, back_uselist=False),
	get_car_trim_link_mixin('specs', nullable=False),
	get_engine_link_mixin('car_specs', nullable=True, on_delete='SET NULL'),
	get_car_transmission_link_mixin('car_specs', nullable=True, on_delete='SET NULL'),
):
	"""
	Спецификация автомобиля (заводские атрибуты конкретного экземпляра).

	Связи:

	- ``vehicle`` — 1:1 с Vehicle (UNIQUE(vehicle_id) + триггер по vehicle_type).
	- ``trim`` — N:1 с CarTrim (заводская комплектация); через него доступны
		generation, series, brand, concern.
	- ``engine`` — N:1 с VehicleEngine, **опционально**: NULL ⇒ фактический
		двигатель совпадает с ``trim.engine``; не-NULL ⇒ двигатель экземпляра
		отличается от заводского (свап).
	- ``transmission`` — N:1 с CarTransmission, **опционально**: аналогично engine.

	Используй ``effective_engine`` / ``effective_transmission`` для
	получения фактического железа (с автоматическим fallback на Trim).
	"""

	vin: Mapped[str] = mapped_column(String(17), doc='VIN-номер')
	body_number: Mapped[str | None] = mapped_column(String(50), doc='Номер кузова')
	number: Mapped[str | None] = mapped_column(String(50), doc='Автомобильный номер')

	__table_args__ = (
		UniqueConstraint('vehicle_id', name='car_spec_vehicle_id_unique'),
		UniqueConstraint('vin', name='car_spec_vin_unique'),
	)

	@property
	def effective_engine(self) -> 'VehicleEngine':
		"""
		Фактический двигатель экземпляра.

		Возвращает ``self.engine`` (свап), если он задан, иначе ``self.trim.engine``
		(заводская конфигурация).
		"""
		return self.engine if self.engine_id is not None else self.trim.engine

	@property
	def effective_transmission(self) -> 'CarTransmission':
		"""
		Фактическая КПП экземпляра.

		Возвращает ``self.transmission`` (свап), если задана, иначе
		``self.trim.transmission``.
		"""
		return self.transmission if self.transmission_id is not None else self.trim.transmission
