"""Репозиторий доступа к данным ``VehicleGeneration`` (поколения ТС)."""

from uuid import UUID

from sqlalchemy import select

from apps.vehicles.models.vehicle.vehicle_generation import VehicleGeneration
from apps.vehicles.repositories.base import BaseRepository


class VehicleGenerationRepository(BaseRepository[VehicleGeneration]):
	"""Доступ к поколениям ТС. Методы поиска возвращают объект или ``None``."""

	model = VehicleGeneration

	async def list_for_series(self, series_id: UUID | None = None) -> list[VehicleGeneration]:
		"""
		Вернуть поколения, отсортированные по году начала продаж (убывание).

		``series_id`` опционально ограничивает выборку серией; без него
		возвращаются все поколения.
		"""
		query = select(VehicleGeneration).order_by(VehicleGeneration.start_year.desc())
		if series_id is not None:
			query = query.where(VehicleGeneration.series_id == series_id)

		return await self._fetch_all(query)
