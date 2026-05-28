from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from fastapi_utils.cbv import cbv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.vehicles.api.reminder.schemas import (
	CreateReminderSchema,
	ReminderDetailSchema,
	UpdateReminderSchema,
)
from apps.vehicles.api.routers import reminder_router
from apps.vehicles.models.vehicle.reminder import VehicleReminder
from apps.vehicles.models.vehicle.user_vehicle import UserVehicle
from common.orm.views.mixins import BaseAPI
from core.db import database


@cbv(reminder_router)
class ReminderAPI(BaseAPI):
	"""API для управления напоминаниями по ТС пользователя."""

	@reminder_router.post(
		'/user-vehicles/{user_vehicle_id}/reminders/',
		response_model=ReminderDetailSchema,
		summary='Создать напоминание',
	)
	async def create_reminder(
		self,
		user_vehicle_id: str,
		data: CreateReminderSchema,
	) -> ReminderDetailSchema:
		"""Создать напоминание для ТС текущего пользователя."""
		async with database.get_async_session() as session:
			await self._get_owned_user_vehicle(session, UUID(user_vehicle_id))

			reminder = VehicleReminder(
				user_id=self.user.id,
				user_vehicle_id=UUID(user_vehicle_id),
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

		return ReminderDetailSchema.model_validate(reminder)

	@reminder_router.get(
		'/user-vehicles/{user_vehicle_id}/reminders/',
		response_model=list[ReminderDetailSchema],
		summary='Список напоминаний ТС',
	)
	async def list_reminders(
		self,
		user_vehicle_id: str,
		is_completed: bool | None = None,
	) -> list[ReminderDetailSchema]:
		"""
		Получить список напоминаний ТС текущего пользователя.

		Параметр ``is_completed`` фильтрует активные/выполненные (историю);
		без него возвращаются все напоминания.
		"""
		async with database.get_async_session() as session:
			await self._get_owned_user_vehicle(session, UUID(user_vehicle_id))

			query = (
				select(VehicleReminder)
				.where(
					VehicleReminder.user_vehicle_id == UUID(user_vehicle_id),
					VehicleReminder.user_id == self.user.id,
				)
				.order_by(VehicleReminder.created_at)
			)
			if is_completed is not None:
				query = query.where(VehicleReminder.is_completed == is_completed)

			reminders = await database.session_fetch_all(session, query)

		return [ReminderDetailSchema.model_validate(reminder) for reminder in reminders]

	@reminder_router.get(
		'/reminders/{reminder_id}/',
		response_model=ReminderDetailSchema,
		summary='Напоминание',
	)
	async def get_reminder(
		self,
		reminder_id: str,
	) -> ReminderDetailSchema:
		"""Получить напоминание текущего пользователя по ID."""
		async with database.get_async_session() as session:
			reminder = await self._get_owned_reminder(session, UUID(reminder_id))

		return ReminderDetailSchema.model_validate(reminder)

	@reminder_router.patch(
		'/reminders/{reminder_id}/',
		response_model=ReminderDetailSchema,
		summary='Редактировать напоминание',
	)
	async def update_reminder(
		self,
		reminder_id: str,
		data: UpdateReminderSchema,
	) -> ReminderDetailSchema:
		"""Частично обновить напоминание (изменяются только переданные поля)."""
		async with database.get_async_session() as session:
			reminder = await self._get_owned_reminder(session, UUID(reminder_id))

			update_data = data.model_dump(exclude_unset=True)
			for field, value in update_data.items():
				setattr(reminder, field, value)

			await session.commit()
			await session.refresh(reminder)

		return ReminderDetailSchema.model_validate(reminder)

	@reminder_router.post(
		'/reminders/{reminder_id}/complete/',
		response_model=ReminderDetailSchema,
		summary='Отметить выполненным',
	)
	async def complete_reminder(
		self,
		reminder_id: str,
	) -> ReminderDetailSchema:
		"""
		Отметить напоминание выполненным.

		Идемпотентно: повторный вызов не меняет исходное время выполнения
		(``completed_at`` проставляется только при первом переходе в статус).
		"""
		async with database.get_async_session() as session:
			reminder = await self._get_owned_reminder(session, UUID(reminder_id))

			if not reminder.is_completed:
				reminder.is_completed = True
				reminder.completed_at = datetime.now(timezone.utc)
				await session.commit()
				await session.refresh(reminder)

		return ReminderDetailSchema.model_validate(reminder)

	@reminder_router.post(
		'/reminders/{reminder_id}/uncomplete/',
		response_model=ReminderDetailSchema,
		summary='Снять отметку о выполнении',
	)
	async def uncomplete_reminder(
		self,
		reminder_id: str,
	) -> ReminderDetailSchema:
		"""Снять отметку о выполнении (вернуть напоминание в активные)."""
		async with database.get_async_session() as session:
			reminder = await self._get_owned_reminder(session, UUID(reminder_id))

			if reminder.is_completed:
				reminder.is_completed = False
				reminder.completed_at = None
				await session.commit()
				await session.refresh(reminder)

		return ReminderDetailSchema.model_validate(reminder)

	@reminder_router.delete(
		'/reminders/{reminder_id}/',
		status_code=status.HTTP_204_NO_CONTENT,
		summary='Удалить напоминание',
	)
	async def delete_reminder(
		self,
		reminder_id: str,
	) -> None:
		"""
		Удалить напоминание текущего пользователя.

		Удаление безусловное; подтверждение удаления (для невыполненных
		напоминаний) реализуется на стороне фронтенда.
		"""
		async with database.get_async_session() as session:
			reminder = await self._get_owned_reminder(session, UUID(reminder_id))
			await session.delete(reminder)
			await session.commit()

	async def _get_owned_user_vehicle(
		self,
		session: AsyncSession,
		user_vehicle_id: UUID,
	) -> UserVehicle:
		"""Загружает ТС текущего пользователя или возбуждает 404."""
		query = select(UserVehicle).where(
			UserVehicle.id == user_vehicle_id,
			UserVehicle.user_id == self.user.id,
		)
		user_vehicle = await database.session_fetch_one(session, query)

		if user_vehicle is None:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail='Транспортное средство не найдено',
			)

		return user_vehicle

	async def _get_owned_reminder(
		self,
		session: AsyncSession,
		reminder_id: UUID,
	) -> VehicleReminder:
		"""Загружает напоминание текущего пользователя или возбуждает 404."""
		query = select(VehicleReminder).where(
			VehicleReminder.id == reminder_id,
			VehicleReminder.user_id == self.user.id,
		)
		reminder = await database.session_fetch_one(session, query)

		if reminder is None:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail='Напоминание не найдено',
			)

		return reminder
