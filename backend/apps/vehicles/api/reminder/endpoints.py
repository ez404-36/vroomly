from uuid import UUID

from fastapi import HTTPException, status
from fastapi_utils.cbv import cbv

from apps.vehicles.api.reminder.mappers import reminder_to_detail, reminders_to_detail
from apps.vehicles.api.reminder.schemas import (
	CreateReminderSchema,
	ReminderDetailSchema,
	UpdateReminderSchema,
)
from apps.vehicles.api.routers import reminder_router
from apps.vehicles.services.reminder import ReminderService
from common.orm.views.mixins import BaseAPI

_VEHICLE_NOT_FOUND = 'Транспортное средство не найдено'
_REMINDER_NOT_FOUND = 'Напоминание не найдено'


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
		reminder = await ReminderService().create(UUID(user_vehicle_id), self.user.id, data)
		if reminder is None:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=_VEHICLE_NOT_FOUND)
		return reminder_to_detail(reminder)

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

		``is_completed`` фильтрует активные/выполненные (историю); без него
		возвращаются все напоминания.
		"""
		reminders = await ReminderService().list_for_vehicle(
			UUID(user_vehicle_id),
			self.user.id,
			is_completed,
		)
		if reminders is None:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=_VEHICLE_NOT_FOUND)
		return reminders_to_detail(reminders)

	@reminder_router.get(
		'/reminders/{reminder_id}/',
		response_model=ReminderDetailSchema,
		summary='Напоминание',
	)
	async def get_reminder(self, reminder_id: str) -> ReminderDetailSchema:
		"""Получить напоминание текущего пользователя по ID."""
		reminder = await ReminderService().get(UUID(reminder_id), self.user.id)
		if reminder is None:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=_REMINDER_NOT_FOUND)
		return reminder_to_detail(reminder)

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
		reminder = await ReminderService().update(UUID(reminder_id), self.user.id, data)
		if reminder is None:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=_REMINDER_NOT_FOUND)
		return reminder_to_detail(reminder)

	@reminder_router.post(
		'/reminders/{reminder_id}/complete/',
		response_model=ReminderDetailSchema,
		summary='Отметить выполненным',
	)
	async def complete_reminder(self, reminder_id: str) -> ReminderDetailSchema:
		"""Отметить напоминание выполненным (идемпотентно)."""
		reminder = await ReminderService().complete(UUID(reminder_id), self.user.id)
		if reminder is None:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=_REMINDER_NOT_FOUND)
		return reminder_to_detail(reminder)

	@reminder_router.post(
		'/reminders/{reminder_id}/uncomplete/',
		response_model=ReminderDetailSchema,
		summary='Снять отметку о выполнении',
	)
	async def uncomplete_reminder(self, reminder_id: str) -> ReminderDetailSchema:
		"""Снять отметку о выполнении (вернуть напоминание в активные)."""
		reminder = await ReminderService().uncomplete(UUID(reminder_id), self.user.id)
		if reminder is None:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=_REMINDER_NOT_FOUND)
		return reminder_to_detail(reminder)

	@reminder_router.delete(
		'/reminders/{reminder_id}/',
		status_code=status.HTTP_204_NO_CONTENT,
		summary='Удалить напоминание',
	)
	async def delete_reminder(self, reminder_id: str) -> None:
		"""
		Удалить напоминание текущего пользователя.

		Удаление безусловное; подтверждение (для невыполненных напоминаний)
		реализуется на стороне фронтенда.
		"""
		deleted = await ReminderService().delete(UUID(reminder_id), self.user.id)
		if not deleted:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=_REMINDER_NOT_FOUND)
