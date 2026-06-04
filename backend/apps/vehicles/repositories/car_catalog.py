"""Репозиторий доступа к каталогу авто для подбора по VIN (бренды/модели/поколения/комплектации)."""

from uuid import UUID

from sqlalchemy import and_, between, select
from sqlalchemy.orm import selectinload

from apps.vehicles.models.car.car_trim import CarTrim
from apps.vehicles.models.vehicle.vehicle_brand import VehicleBrand
from apps.vehicles.models.vehicle.vehicle_generation import VehicleGeneration
from apps.vehicles.models.vehicle.vehicle_series import VehicleSeries
from apps.vehicles.repositories.fuzzy_lookup import fuzzy_lookup
from core.db import database


class CarCatalogRepository:
	"""Подбор сущностей каталога авто (с нечётким поиском бренда/модели)."""

	async def find_brand(self, brand_name: str) -> VehicleBrand | None:
		"""Найти бренд по (переведённому) названию через нечёткий поиск."""
		return await fuzzy_lookup(VehicleBrand, brand_name)

	async def find_series(self, brand_id: UUID, series_name: str) -> VehicleSeries | None:
		"""Найти модель/серию бренда по (переведённому) названию через нечёткий поиск."""
		return await fuzzy_lookup(
			VehicleSeries,
			series_name,
			extra_where=VehicleSeries.brand_id == brand_id,
		)

	async def list_generations(self, series_id: UUID, production_year: int) -> list[VehicleGeneration]:
		"""Вернуть поколения серии, в чей диапазон годов попадает ``production_year``."""
		query = select(VehicleGeneration).where(
			and_(
				VehicleGeneration.series_id == series_id,
				between(production_year, VehicleGeneration.start_year, VehicleGeneration.end_year),
			)
		)
		return list(await database.fetch_all(query))

	async def list_trims(self, generation_ids: list[UUID]) -> list[CarTrim]:
		"""Вернуть комплектации указанных поколений с подгруженными узлами."""
		if not generation_ids:
			return []

		query = (
			select(CarTrim)
			.where(CarTrim.generation_id.in_(generation_ids))
			.options(
				selectinload(CarTrim.generation),
				selectinload(CarTrim.engine),
				selectinload(CarTrim.transmission),
				selectinload(CarTrim.body),
			)
		)
		return list(await database.fetch_all(query))
