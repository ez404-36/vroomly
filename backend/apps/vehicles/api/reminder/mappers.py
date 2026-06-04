"""Преобразование ORM ``VehicleReminder`` → Pydantic-схемы.

Слой представления: маппинг ORM-объектов в Detail-схему. Не содержит ни
доступа к данным, ни бизнес-логики.
"""

from apps.vehicles.api.reminder.schemas import ReminderDetailSchema
from apps.vehicles.models.vehicle.reminder import VehicleReminder


def reminder_to_detail(reminder: VehicleReminder) -> ReminderDetailSchema:
	"""Конвертирует ORM ``VehicleReminder`` в Detail-схему."""
	return ReminderDetailSchema.model_validate(reminder)


def reminders_to_detail(reminders: list[VehicleReminder]) -> list[ReminderDetailSchema]:
	"""Конвертирует список ORM ``VehicleReminder`` в список Detail-схем."""
	return [reminder_to_detail(reminder) for reminder in reminders]
