from datetime import datetime
from typing import Any

from fastapi_utils.api_model import APIModel
from pydantic import Field, model_validator


class CreateReminderSchema(APIModel):
	"""
	Схема входа для создания напоминания по ТС.

	Привязка к ``UserVehicle`` берётся из пути запроса, поэтому в теле
	передаются только данные самого напоминания.
	"""

	title: str = Field(min_length=1, max_length=100, description='Суть напоминания')
	description: str | None = Field(default=None, max_length=500, description='Детали напоминания')
	due_at: datetime | None = Field(default=None, description='Дата/время выполнения')
	is_all_day: bool = Field(default=False, description='Напоминание на весь день (без времени)')


class UpdateReminderSchema(APIModel):
	"""
	Схема частичного обновления напоминания.

	Все поля опциональны. Передаются только изменяемые поля; на стороне
	эндпоинта применяется ``model_dump(exclude_unset=True)``, поэтому
	неуказанные поля остаются без изменений, а явно переданный ``null``
	(например, ``due_at``) очищает значение.
	"""

	title: str | None = Field(default=None, min_length=1, max_length=100, description='Суть напоминания')
	description: str | None = Field(default=None, max_length=500, description='Детали напоминания')
	due_at: datetime | None = Field(default=None, description='Дата/время выполнения')
	is_all_day: bool | None = Field(default=None, description='Напоминание на весь день (без времени)')


class ReminderDetailSchema(APIModel):
	"""Схема для отображения напоминания по ТС."""

	id: str = Field(description='ID напоминания')
	user_vehicle_id: str = Field(description='ID ТС пользователя')
	title: str = Field(description='Суть напоминания')
	description: str | None = Field(default=None, description='Детали напоминания')
	due_at: datetime | None = Field(default=None, description='Дата/время выполнения')
	is_all_day: bool = Field(description='Напоминание на весь день (без времени)')
	is_completed: bool = Field(description='Напоминание выполнено')
	completed_at: datetime | None = Field(default=None, description='Дата/время отметки о выполнении')
	created_at: datetime = Field(description='Дата/время создания')
	updated_at: datetime | None = Field(default=None, description='Дата/время последнего изменения')

	@model_validator(mode='before')
	@classmethod
	def convert_reminder(cls, data: Any) -> Any:
		"""
		Конвертирует ORM ``VehicleReminder`` в плоский dict для схемы.

		UUID-поля приводятся к строке; остальные поля передаются как есть.
		Если на вход пришёл не ORM-объект (нет ``id``) — возвращаем без изменений.
		"""
		if not hasattr(data, 'id'):
			return data

		return {
			'id': str(data.id),
			'user_vehicle_id': str(data.user_vehicle_id) if data.user_vehicle_id else None,
			'title': data.title,
			'description': data.description,
			'due_at': data.due_at,
			'is_all_day': data.is_all_day,
			'is_completed': data.is_completed,
			'completed_at': data.completed_at,
			'created_at': data.created_at,
			'updated_at': data.updated_at,
		}
