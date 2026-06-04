"""Репозиторий доступа к данным ``VehicleReminder`` (напоминания по ТС)."""

from uuid import UUID

from sqlalchemy import select

from apps.vehicles.models.vehicle.reminder import VehicleReminder
from apps.vehicles.repositories.base import BaseRepository


class ReminderRepository(BaseRepository[VehicleReminder]):
	"""Доступ к напоминаниям пользователя. Методы поиска возвращают объект или ``None``."""

	model = VehicleReminder

	async def get_owned(self, reminder_id: UUID, user_id: UUID) -> VehicleReminder | None:
		"""
		Вернуть напоминание пользователя или ``None``.

		Проверка владения — фильтр ``user_id`` в запросе; HTTP-семантика (404)
		остаётся в слое эндпоинтов.
		"""
		query = select(VehicleReminder).where(
			VehicleReminder.id == reminder_id,
			VehicleReminder.user_id == user_id,
		)
		return await self._fetch_one(query)

	async def list_for_vehicle(
		self,
		user_vehicle_id: UUID,
		user_id: UUID,
		is_completed: bool | None = None,
	) -> list[VehicleReminder]:
		"""
		Вернуть напоминания ТС пользователя, отсортированные по дате создания.

		``is_completed`` опционально фильтрует активные/выполненные; без него
		возвращаются все напоминания.
		"""
		query = (
			select(VehicleReminder)
			.where(
				VehicleReminder.user_vehicle_id == user_vehicle_id,
				VehicleReminder.user_id == user_id,
			)
			.order_by(VehicleReminder.created_at)
		)
		if is_completed is not None:
			query = query.where(VehicleReminder.is_completed == is_completed)

		return await self._fetch_all(query)
