"""Репозиторий доступа к данным ``VehicleSeries`` (модели ТС)."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from apps.vehicles.models.vehicle.vehicle_series import VehicleSeries
from apps.vehicles.repositories.base import BaseRepository
from common.orm.filters import apply_search

_SEARCH_FIELDS: tuple[str, ...] = ('name',)


class VehicleSeriesRepository(BaseRepository[VehicleSeries]):
	"""Доступ к моделям ТС. Методы поиска возвращают объект или ``None``."""

	model = VehicleSeries

	async def list_filtered(
		self,
		brand_id: UUID | None = None,
		search: str | None = None,
	) -> list[VehicleSeries]:
		"""
		Вернуть модели, отсортированные по названию.

		``search`` применяет ILIKE-поиск по названию, ``brand_id`` ограничивает
		выборку брендом.
		"""
		query = apply_search(
			select(VehicleSeries).order_by(VehicleSeries.name.asc()),
			search,
			_SEARCH_FIELDS,
		)
		if brand_id is not None:
			query = query.filter(VehicleSeries.brand_id == brand_id)

		return await self._fetch_all(query)

	async def get_with_brand(self, series_id: UUID) -> VehicleSeries | None:
		"""Вернуть модель с подгруженным брендом (``joinedload``) или ``None``."""
		query = select(VehicleSeries).options(joinedload(VehicleSeries.brand)).where(VehicleSeries.id == series_id)
		return await self._fetch_one(query)
