"""Репозиторий доступа к данным ``VehicleBrand`` (марки ТС)."""

from typing import Literal

from sqlalchemy import select

from apps.vehicles.models.vehicle.vehicle_brand import VehicleBrand
from apps.vehicles.repositories.base import BaseRepository
from common.orm.filters import apply_search

_SEARCH_FIELDS: tuple[str, ...] = ('code',)

BrandOrdering = Literal['country_id', 'code']


class VehicleBrandRepository(BaseRepository[VehicleBrand]):
	"""Доступ к маркам ТС. Методы поиска возвращают объект или ``None``."""

	model = VehicleBrand

	async def list_filtered(
		self,
		ordering: BrandOrdering = 'code',
		search: str | None = None,
		country: str | None = None,
	) -> list[VehicleBrand]:
		"""
		Вернуть марки, отсортированные по ``ordering``.

		``search`` применяет ILIKE-поиск по коду; ``country`` фильтрует по коду
		страны (нормализуется в верхний регистр перед сравнением).
		"""
		query = apply_search(
			select(VehicleBrand).order_by(ordering),
			search,
			_SEARCH_FIELDS,
		)
		if country:
			query = query.filter(VehicleBrand.country_id == country.upper())

		return await self._fetch_all(query)
