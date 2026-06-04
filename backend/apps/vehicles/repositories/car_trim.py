"""Репозиторий доступа к данным ``CarTrim`` (комплектации)."""

from uuid import UUID

from sqlalchemy import select

from apps.vehicles.models.car.car_trim import CarTrim
from apps.vehicles.repositories.base import BaseRepository


class CarTrimRepository(BaseRepository[CarTrim]):
	"""Доступ к комплектациям. Методы поиска возвращают объект или ``None``."""

	model = CarTrim

	async def list_for_generation(self, generation_id: UUID | None = None) -> list[CarTrim]:
		"""
		Вернуть комплектации, отсортированные по названию.

		``generation_id`` опционально ограничивает выборку поколением; без него
		возвращаются все комплектации.
		"""
		query = select(CarTrim).order_by(CarTrim.name.asc())
		if generation_id is not None:
			query = query.where(CarTrim.generation_id == generation_id)

		return await self._fetch_all(query)
