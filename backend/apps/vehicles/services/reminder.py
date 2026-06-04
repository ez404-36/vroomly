"""Бизнес-логика напоминаний по ТС пользователя (``VehicleReminder``).

Сервис владеет транзакциями, проверками владения и инвариантами
(идемпотентные complete/uncomplete, частичное обновление). Он не знает про HTTP:
методы возвращают ORM-объект / ``None`` (нет доступа или записи), а преобразование
``None`` → ``404`` — задача слоя эндпоинтов.
"""

from datetime import datetime, timezone
from uuid import UUID

from apps.vehicles.api.reminder.schemas import CreateReminderSchema, UpdateReminderSchema
from apps.vehicles.models.vehicle.reminder import VehicleReminder
from apps.vehicles.repositories.reminder import ReminderRepository
from apps.vehicles.repositories.user_vehicle import UserVehicleRepository
from core.db import database


class ReminderService:
	"""Создание, чтение, обновление и удаление напоминаний по ТС."""

	async def create(
		self,
		user_vehicle_id: UUID,
		user_id: UUID,
		data: CreateReminderSchema,
	) -> VehicleReminder | None:
		"""
		Создать напоминание для ТС пользователя.

		:returns: созданное напоминание; ``None``, если ТС не принадлежит
			пользователю (или не существует).
		"""
		async with database.get_async_session() as session:
			owned = await UserVehicleRepository(session).get_owned(user_vehicle_id, user_id)
			if owned is None:
				return None

			reminder = VehicleReminder(
				user_id=user_id,
				user_vehicle_id=user_vehicle_id,
				title=data.title,
				description=data.description,
				due_at=data.due_at,
				is_all_day=data.is_all_day,
				is_completed=False,
				completed_at=None,
			)
			session.add(reminder)
			await session.commit()
			await session.refresh(reminder)
			return reminder

	async def list_for_vehicle(
		self,
		user_vehicle_id: UUID,
		user_id: UUID,
		is_completed: bool | None = None,
	) -> list[VehicleReminder] | None:
		"""
		Вернуть напоминания ТС пользователя.

		:returns: список напоминаний; ``None``, если ТС не принадлежит
			пользователю (или не существует).
		"""
		async with database.get_async_session() as session:
			owned = await UserVehicleRepository(session).get_owned(user_vehicle_id, user_id)
			if owned is None:
				return None

			return await ReminderRepository(session).list_for_vehicle(
				user_vehicle_id,
				user_id,
				is_completed,
			)

	async def get(self, reminder_id: UUID, user_id: UUID) -> VehicleReminder | None:
		"""Вернуть напоминание пользователя или ``None``."""
		return await ReminderRepository().get_owned(reminder_id, user_id)

	async def update(
		self,
		reminder_id: UUID,
		user_id: UUID,
		data: UpdateReminderSchema,
	) -> VehicleReminder | None:
		"""
		Частично обновить напоминание (изменяются только переданные поля).

		:returns: обновлённое напоминание; ``None``, если оно не найдено / чужое.
		"""
		async with database.get_async_session() as session:
			reminder = await ReminderRepository(session).get_owned(reminder_id, user_id)
			if reminder is None:
				return None

			update_data = data.model_dump(exclude_unset=True)
			for field, value in update_data.items():
				setattr(reminder, field, value)

			await session.commit()
			await session.refresh(reminder)
			return reminder

	async def complete(self, reminder_id: UUID, user_id: UUID) -> VehicleReminder | None:
		"""
		Отметить напоминание выполненным (идемпотентно).

		Повторный вызов не меняет исходное ``completed_at``.

		:returns: напоминание; ``None``, если оно не найдено / чужое.
		"""
		async with database.get_async_session() as session:
			reminder = await ReminderRepository(session).get_owned(reminder_id, user_id)
			if reminder is None:
				return None

			if not reminder.is_completed:
				reminder.is_completed = True
				reminder.completed_at = datetime.now(timezone.utc)
				await session.commit()
				await session.refresh(reminder)
			return reminder

	async def uncomplete(self, reminder_id: UUID, user_id: UUID) -> VehicleReminder | None:
		"""
		Снять отметку о выполнении (идемпотентно).

		:returns: напоминание; ``None``, если оно не найдено / чужое.
		"""
		async with database.get_async_session() as session:
			reminder = await ReminderRepository(session).get_owned(reminder_id, user_id)
			if reminder is None:
				return None

			if reminder.is_completed:
				reminder.is_completed = False
				reminder.completed_at = None
				await session.commit()
				await session.refresh(reminder)
			return reminder

	async def delete(self, reminder_id: UUID, user_id: UUID) -> bool:
		"""
		Удалить напоминание пользователя.

		:returns: ``True`` если удалено; ``False`` если не найдено / чужое.
		"""
		async with database.get_async_session() as session:
			reminder = await ReminderRepository(session).get_owned(reminder_id, user_id)
			if reminder is None:
				return False

			await session.delete(reminder)
			await session.commit()
			return True
