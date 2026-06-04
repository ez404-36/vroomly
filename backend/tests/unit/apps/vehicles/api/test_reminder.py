"""Tests for VehicleReminder API schemas and endpoint delegation.

После выделения слоёв (Фаза 2) бизнес-логика и доступ к данным живут в
``ReminderService``/репозиториях. Эндпоинты — тонкие: делегируют сервису и
маппят ``None`` → 404. Здесь тестируются:

- валидация схем (вход/выход);
- делегирование эндпоинтов сервису и маппинг 404.

Бизнес-логика (идемпотентность, проверки владения) покрыта в
``tests/unit/apps/vehicles/services/test_reminder_service.py``.
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Coroutine, TypeVar
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from apps.vehicles.api.reminder.endpoints import ReminderAPI
from apps.vehicles.api.reminder.schemas import (
	CreateReminderSchema,
	ReminderDetailSchema,
	UpdateReminderSchema,
)

T = TypeVar('T')

_SERVICE_PATH = 'apps.vehicles.api.reminder.endpoints.ReminderService'


def _run(coro: Coroutine[Any, Any, T]) -> T:
	"""Запускает корутину в свежем event loop (без pytest-asyncio)."""
	return asyncio.run(coro)


def _make_api(user_id: Any = None) -> ReminderAPI:
	"""Создаёт экземпляр CBV-класса без вызова FastAPI-инициализации."""
	api = ReminderAPI.__new__(ReminderAPI)
	api.user = MagicMock(id=user_id if user_id is not None else uuid4())
	return api


def _make_reminder_orm(**overrides: Any) -> MagicMock:
	"""Создаёт ORM-подобный объект VehicleReminder для конвертера/эндпоинтов."""
	defaults: dict[str, Any] = {
		'id': uuid4(),
		'user_id': uuid4(),
		'user_vehicle_id': uuid4(),
		'title': 'Замена масла',
		'description': 'Каждые 10000 км',
		'due_at': datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc),
		'is_all_day': False,
		'is_completed': False,
		'completed_at': None,
		'created_at': datetime(2026, 5, 1, 9, 0, tzinfo=timezone.utc),
		'updated_at': None,
	}
	defaults.update(overrides)
	return MagicMock(**defaults)


def _patch_service(**methods: Any) -> Any:
	"""Патчит ReminderService так, что service() возвращает mock с заданными методами."""
	service = MagicMock()
	for name, value in methods.items():
		setattr(service, name, value)
	return patch(_SERVICE_PATH, return_value=service)


class TestCreateReminderSchema:
	"""Tests for CreateReminderSchema validation."""

	def test_minimal_valid_data(self):
		"""Только title обязателен; остальные поля имеют значения по умолчанию."""
		schema = CreateReminderSchema(title='Замена масла')
		assert schema.title == 'Замена масла'
		assert schema.description is None
		assert schema.due_at is None
		assert schema.is_all_day is False

	def test_full_valid_data(self):
		"""Все поля задаются успешно."""
		due = datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc)
		schema = CreateReminderSchema(
			title='Замена масла',
			description='Каждые 10000 км',
			due_at=due,
			is_all_day=True,
		)
		assert schema.description == 'Каждые 10000 км'
		assert schema.due_at == due
		assert schema.is_all_day is True

	def test_due_at_accepts_none(self):
		"""due_at принимает None."""
		schema = CreateReminderSchema(title='Без даты', due_at=None)
		assert schema.due_at is None

	def test_title_required(self):
		"""Без title — ошибка валидации."""
		with pytest.raises(Exception):
			CreateReminderSchema.model_validate({})

	def test_empty_title_rejected(self):
		"""Пустой title (min_length=1) — ошибка."""
		with pytest.raises(Exception):
			CreateReminderSchema(title='')

	def test_title_too_long_rejected(self):
		"""Title длиннее 100 символов — ошибка."""
		with pytest.raises(Exception):
			CreateReminderSchema(title='x' * 101)

	def test_description_too_long_rejected(self):
		"""Description длиннее 500 символов — ошибка."""
		with pytest.raises(Exception):
			CreateReminderSchema(title='Замена масла', description='x' * 501)


class TestUpdateReminderSchema:
	"""Tests for UpdateReminderSchema (partial-update contract)."""

	def test_all_fields_optional(self):
		"""Конструируется без полей; все значения по умолчанию None."""
		schema = UpdateReminderSchema()
		assert schema.title is None
		assert schema.description is None
		assert schema.due_at is None
		assert schema.is_all_day is None

	def test_exclude_unset_returns_only_provided_fields(self):
		"""model_dump(exclude_unset=True) содержит только переданные поля."""
		schema = UpdateReminderSchema(title='Новое название')
		dumped = schema.model_dump(exclude_unset=True)
		assert dumped == {'title': 'Новое название'}
		assert 'description' not in dumped
		assert 'due_at' not in dumped
		assert 'is_all_day' not in dumped

	def test_explicit_none_is_present_in_dump(self):
		"""Явно переданный null присутствует в dump (семантика очистки поля)."""
		schema = UpdateReminderSchema(due_at=None)
		dumped = schema.model_dump(exclude_unset=True)
		assert 'due_at' in dumped
		assert dumped['due_at'] is None

	def test_invalid_title_length_rejected(self):
		"""Невалидная длина title — ошибка даже при частичном обновлении."""
		with pytest.raises(Exception):
			UpdateReminderSchema(title='x' * 101)

	def test_empty_title_rejected(self):
		"""Пустой title (min_length=1) — ошибка."""
		with pytest.raises(Exception):
			UpdateReminderSchema(title='')


class TestReminderDetailSchemaConverter:
	"""Tests for ReminderDetailSchema.convert_reminder (model_validator)."""

	def test_convert_from_orm(self):
		"""Конвертирует ORM-объект: UUID → строка, остальные поля как есть."""
		reminder_id = uuid4()
		user_vehicle_id = uuid4()
		due = datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc)
		created = datetime(2026, 5, 1, 9, 0, tzinfo=timezone.utc)
		orm = _make_reminder_orm(
			id=reminder_id,
			user_vehicle_id=user_vehicle_id,
			title='Замена масла',
			description='Каждые 10000 км',
			due_at=due,
			is_all_day=False,
			is_completed=True,
			completed_at=created,
			created_at=created,
			updated_at=None,
		)

		schema = ReminderDetailSchema.model_validate(orm)
		assert schema.id == str(reminder_id)
		assert schema.user_vehicle_id == str(user_vehicle_id)
		assert schema.title == 'Замена масла'
		assert schema.description == 'Каждые 10000 км'
		assert schema.due_at == due
		assert schema.is_all_day is False
		assert schema.is_completed is True
		assert schema.completed_at == created
		assert schema.created_at == created
		assert schema.updated_at is None

	def test_convert_preserves_none_due_at_and_completed_at(self):
		"""None в due_at/completed_at сохраняется."""
		orm = _make_reminder_orm(due_at=None, completed_at=None, description=None)
		schema = ReminderDetailSchema.model_validate(orm)
		assert schema.due_at is None
		assert schema.completed_at is None
		assert schema.description is None

	def test_guard_returns_dict_unchanged(self):
		"""Dict без атрибута id возвращается без изменений (ветка-гард)."""
		data = {
			'id': '123e4567-e89b-12d3-a456-426614174000',
			'user_vehicle_id': '123e4567-e89b-12d3-a456-426614174001',
			'title': 'Из dict',
			'is_all_day': False,
			'is_completed': False,
			'created_at': datetime(2026, 5, 1, 9, 0, tzinfo=timezone.utc),
		}
		schema = ReminderDetailSchema.model_validate(data)
		assert schema.id == '123e4567-e89b-12d3-a456-426614174000'
		assert schema.title == 'Из dict'


class TestCreateReminderEndpoint:
	"""create_reminder: делегирование сервису + маппинг 404."""

	def test_delegates_and_maps_result(self):
		"""Эндпоинт зовёт service.create и возвращает Detail-схему."""
		user_id = uuid4()
		user_vehicle_id = uuid4()
		api = _make_api(user_id)
		orm = _make_reminder_orm(title='Замена масла')
		data = CreateReminderSchema(title='Замена масла', is_all_day=True)

		create = AsyncMock(return_value=orm)
		with _patch_service(create=create):
			result = _run(api.create_reminder(user_vehicle_id=str(user_vehicle_id), data=data))

		assert isinstance(result, ReminderDetailSchema)
		assert result.title == 'Замена масла'
		create.assert_awaited_once_with(user_vehicle_id, user_id, data)

	def test_foreign_vehicle_raises_404(self):
		"""service.create вернул None (чужое ТС) → 404."""
		api = _make_api()
		data = CreateReminderSchema(title='Замена масла')

		with _patch_service(create=AsyncMock(return_value=None)):
			with pytest.raises(HTTPException) as exc_info:
				_run(api.create_reminder(user_vehicle_id=str(uuid4()), data=data))

		assert exc_info.value.status_code == 404


class TestListRemindersEndpoint:
	"""list_reminders: делегирование + маппинг 404."""

	def test_returns_mapped_list(self):
		"""Возвращает список ReminderDetailSchema."""
		api = _make_api()
		reminders = [_make_reminder_orm(), _make_reminder_orm()]

		with _patch_service(list_for_vehicle=AsyncMock(return_value=reminders)):
			result = _run(api.list_reminders(user_vehicle_id=str(uuid4())))

		assert len(result) == 2
		assert all(isinstance(item, ReminderDetailSchema) for item in result)

	def test_passes_is_completed_filter(self):
		"""Параметр is_completed пробрасывается в сервис."""
		api = _make_api()
		uv_id = uuid4()
		list_for_vehicle = AsyncMock(return_value=[_make_reminder_orm(is_completed=True)])

		with _patch_service(list_for_vehicle=list_for_vehicle):
			result = _run(api.list_reminders(user_vehicle_id=str(uv_id), is_completed=True))

		list_for_vehicle.assert_awaited_once_with(uv_id, api.user.id, True)
		assert result[0].is_completed is True

	def test_foreign_vehicle_raises_404(self):
		"""service.list_for_vehicle вернул None → 404."""
		api = _make_api()
		with _patch_service(list_for_vehicle=AsyncMock(return_value=None)):
			with pytest.raises(HTTPException) as exc_info:
				_run(api.list_reminders(user_vehicle_id=str(uuid4())))

		assert exc_info.value.status_code == 404


class TestGetReminderEndpoint:
	"""get_reminder: делегирование + 404."""

	def test_returns_owned_reminder(self):
		api = _make_api()
		orm = _make_reminder_orm(title='Проверить тормоза')
		with _patch_service(get=AsyncMock(return_value=orm)):
			result = _run(api.get_reminder(reminder_id=str(uuid4())))

		assert isinstance(result, ReminderDetailSchema)
		assert result.title == 'Проверить тормоза'

	def test_missing_reminder_raises_404(self):
		api = _make_api()
		with _patch_service(get=AsyncMock(return_value=None)):
			with pytest.raises(HTTPException) as exc_info:
				_run(api.get_reminder(reminder_id=str(uuid4())))

		assert exc_info.value.status_code == 404


class TestUpdateReminderEndpoint:
	"""update_reminder: делегирование + 404."""

	def test_delegates_with_data(self):
		api = _make_api()
		orm = _make_reminder_orm(title='Новое название')
		data = UpdateReminderSchema(title='Новое название')
		update = AsyncMock(return_value=orm)

		with _patch_service(update=update):
			result = _run(api.update_reminder(reminder_id=str(uuid4()), data=data))

		assert result.title == 'Новое название'
		update.assert_awaited_once()

	def test_missing_reminder_raises_404(self):
		api = _make_api()
		data = UpdateReminderSchema(title='Новое')
		with _patch_service(update=AsyncMock(return_value=None)):
			with pytest.raises(HTTPException) as exc_info:
				_run(api.update_reminder(reminder_id=str(uuid4()), data=data))

		assert exc_info.value.status_code == 404


class TestCompleteUncompleteEndpoints:
	"""complete/uncomplete: делегирование + 404."""

	def test_complete_returns_schema(self):
		api = _make_api()
		orm = _make_reminder_orm(is_completed=True)
		with _patch_service(complete=AsyncMock(return_value=orm)):
			result = _run(api.complete_reminder(reminder_id=str(uuid4())))
		assert result.is_completed is True

	def test_complete_missing_raises_404(self):
		api = _make_api()
		with _patch_service(complete=AsyncMock(return_value=None)):
			with pytest.raises(HTTPException) as exc_info:
				_run(api.complete_reminder(reminder_id=str(uuid4())))
		assert exc_info.value.status_code == 404

	def test_uncomplete_returns_schema(self):
		api = _make_api()
		orm = _make_reminder_orm(is_completed=False)
		with _patch_service(uncomplete=AsyncMock(return_value=orm)):
			result = _run(api.uncomplete_reminder(reminder_id=str(uuid4())))
		assert result.is_completed is False

	def test_uncomplete_missing_raises_404(self):
		api = _make_api()
		with _patch_service(uncomplete=AsyncMock(return_value=None)):
			with pytest.raises(HTTPException) as exc_info:
				_run(api.uncomplete_reminder(reminder_id=str(uuid4())))
		assert exc_info.value.status_code == 404


class TestDeleteReminderEndpoint:
	"""delete_reminder: делегирование + 404."""

	def test_deletes_when_service_returns_true(self):
		api = _make_api()
		delete = AsyncMock(return_value=True)
		with _patch_service(delete=delete):
			result = _run(api.delete_reminder(reminder_id=str(uuid4())))
		assert result is None
		delete.assert_awaited_once()

	def test_missing_reminder_raises_404(self):
		api = _make_api()
		with _patch_service(delete=AsyncMock(return_value=False)):
			with pytest.raises(HTTPException) as exc_info:
				_run(api.delete_reminder(reminder_id=str(uuid4())))
		assert exc_info.value.status_code == 404
