"""Tests for VehicleReminder API schemas and endpoint logic."""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Coroutine, TypeVar
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

_DB_PATH = 'apps.vehicles.api.reminder.endpoints.database'


def _run(coro: Coroutine[Any, Any, T]) -> T:
	"""Запускает корутину в свежем event loop (без pytest-asyncio)."""
	return asyncio.run(coro)


def _make_api(user_id: Any = None) -> ReminderAPI:
	"""Создаёт экземпляр CBV-класса без вызова FastAPI-инициализации."""
	api = ReminderAPI.__new__(ReminderAPI)
	api.user = MagicMock(id=user_id if user_id is not None else uuid4())
	return api


def _make_session() -> MagicMock:
	"""Мокает AsyncSession с async-методами add/commit/refresh/delete.

	``refresh`` имитирует заполнение БД-значений по умолчанию (``id`` и
	``created_at`` обычно проставляются на стороне СУБД при commit), чтобы
	созданный ORM-объект мог быть сериализован схемой.
	"""
	session = MagicMock()
	session.add = MagicMock()
	session.commit = AsyncMock()
	session.delete = AsyncMock()

	async def _refresh(instance: Any) -> None:
		if getattr(instance, 'id', None) is None:
			instance.id = uuid4()
		if getattr(instance, 'created_at', None) is None:
			instance.created_at = datetime(2026, 5, 1, 9, 0, tzinfo=timezone.utc)

	session.refresh = AsyncMock(side_effect=_refresh)
	return session


def _patch_session(database_mock: MagicMock, session: MagicMock) -> None:
	"""Настраивает database.get_async_session() как async-context-manager."""

	@asynccontextmanager
	async def _ctx() -> AsyncIterator[MagicMock]:
		yield session

	database_mock.get_async_session.side_effect = _ctx


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
	"""Tests for ReminderAPI.create_reminder."""

	def test_creates_reminder_for_owned_vehicle(self):
		"""При владении ТС создаёт VehicleReminder с user_id текущего пользователя."""
		user_id = uuid4()
		user_vehicle_id = uuid4()
		api = _make_api(user_id)
		session = _make_session()
		data = CreateReminderSchema(title='Замена масла', is_all_day=True)

		with patch(_DB_PATH) as db:
			_patch_session(db, session)
			db.session_fetch_one = AsyncMock(return_value=MagicMock(id=user_vehicle_id))
			result = _run(api.create_reminder(user_vehicle_id=str(user_vehicle_id), data=data))

		assert isinstance(result, ReminderDetailSchema)
		session.add.assert_called_once()
		added = session.add.call_args.args[0]
		assert added.user_id == user_id
		assert added.user_vehicle_id == user_vehicle_id
		assert added.title == 'Замена масла'
		assert added.is_all_day is True
		assert added.is_completed is False
		assert added.completed_at is None
		session.commit.assert_awaited_once()

	def test_foreign_vehicle_raises_404(self):
		"""Чужое/несуществующее ТС → 404, напоминание не создаётся."""
		api = _make_api()
		session = _make_session()
		data = CreateReminderSchema(title='Замена масла')

		with patch(_DB_PATH) as db:
			_patch_session(db, session)
			db.session_fetch_one = AsyncMock(return_value=None)
			with pytest.raises(HTTPException) as exc_info:
				_run(api.create_reminder(user_vehicle_id=str(uuid4()), data=data))

		assert exc_info.value.status_code == 404
		session.add.assert_not_called()


class TestListRemindersEndpoint:
	"""Tests for ReminderAPI.list_reminders."""

	def test_returns_mapped_list(self):
		"""Возвращает список ReminderDetailSchema для напоминаний ТС."""
		api = _make_api()
		session = _make_session()
		reminders = [_make_reminder_orm(), _make_reminder_orm()]

		with patch(_DB_PATH) as db:
			_patch_session(db, session)
			db.session_fetch_one = AsyncMock(return_value=MagicMock())
			db.session_fetch_all = AsyncMock(return_value=reminders)
			result = _run(api.list_reminders(user_vehicle_id=str(uuid4())))

		assert len(result) == 2
		assert all(isinstance(item, ReminderDetailSchema) for item in result)

	def test_filter_by_is_completed(self):
		"""С фильтром is_completed=True вызывается выборка истории."""
		api = _make_api()
		session = _make_session()
		completed = _make_reminder_orm(is_completed=True)

		with patch(_DB_PATH) as db:
			_patch_session(db, session)
			db.session_fetch_one = AsyncMock(return_value=MagicMock())
			db.session_fetch_all = AsyncMock(return_value=[completed])
			result = _run(
				api.list_reminders(user_vehicle_id=str(uuid4()), is_completed=True),
			)

		db.session_fetch_all.assert_awaited_once()
		assert len(result) == 1
		assert result[0].is_completed is True

	def test_foreign_vehicle_raises_404(self):
		"""Чужое ТС → 404, список не запрашивается."""
		api = _make_api()
		session = _make_session()

		with patch(_DB_PATH) as db:
			_patch_session(db, session)
			db.session_fetch_one = AsyncMock(return_value=None)
			db.session_fetch_all = AsyncMock()
			with pytest.raises(HTTPException) as exc_info:
				_run(api.list_reminders(user_vehicle_id=str(uuid4())))

		assert exc_info.value.status_code == 404
		db.session_fetch_all.assert_not_awaited()


class TestGetReminderEndpoint:
	"""Tests for ReminderAPI.get_reminder."""

	def test_returns_owned_reminder(self):
		"""Возвращает напоминание текущего пользователя."""
		api = _make_api()
		session = _make_session()
		orm = _make_reminder_orm(title='Проверить тормоза')

		with patch(_DB_PATH) as db:
			_patch_session(db, session)
			db.session_fetch_one = AsyncMock(return_value=orm)
			result = _run(api.get_reminder(reminder_id=str(uuid4())))

		assert isinstance(result, ReminderDetailSchema)
		assert result.title == 'Проверить тормоза'

	def test_missing_reminder_raises_404(self):
		"""Отсутствующее/чужое напоминание → 404."""
		api = _make_api()
		session = _make_session()

		with patch(_DB_PATH) as db:
			_patch_session(db, session)
			db.session_fetch_one = AsyncMock(return_value=None)
			with pytest.raises(HTTPException) as exc_info:
				_run(api.get_reminder(reminder_id=str(uuid4())))

		assert exc_info.value.status_code == 404


class TestUpdateReminderEndpoint:
	"""Tests for ReminderAPI.update_reminder."""

	def test_applies_only_provided_fields(self):
		"""Применяются только переданные поля (exclude_unset)."""
		api = _make_api()
		session = _make_session()
		orm = _make_reminder_orm(title='Старое', description='Старое описание')
		data = UpdateReminderSchema(title='Новое название')

		with patch(_DB_PATH) as db:
			_patch_session(db, session)
			db.session_fetch_one = AsyncMock(return_value=orm)
			_run(api.update_reminder(reminder_id=str(uuid4()), data=data))

		assert orm.title == 'Новое название'
		assert orm.description == 'Старое описание'
		session.commit.assert_awaited_once()

	def test_explicit_none_clears_field(self):
		"""Явный null очищает поле (due_at=None)."""
		api = _make_api()
		session = _make_session()
		orm = _make_reminder_orm(due_at=datetime(2026, 6, 1, tzinfo=timezone.utc))
		data = UpdateReminderSchema(due_at=None)

		with patch(_DB_PATH) as db:
			_patch_session(db, session)
			db.session_fetch_one = AsyncMock(return_value=orm)
			_run(api.update_reminder(reminder_id=str(uuid4()), data=data))

		assert orm.due_at is None

	def test_missing_reminder_raises_404(self):
		"""Отсутствующее напоминание → 404, изменений нет."""
		api = _make_api()
		session = _make_session()
		data = UpdateReminderSchema(title='Новое')

		with patch(_DB_PATH) as db:
			_patch_session(db, session)
			db.session_fetch_one = AsyncMock(return_value=None)
			with pytest.raises(HTTPException) as exc_info:
				_run(api.update_reminder(reminder_id=str(uuid4()), data=data))

		assert exc_info.value.status_code == 404
		session.commit.assert_not_awaited()


class TestCompleteReminderEndpoint:
	"""Tests for ReminderAPI.complete_reminder."""

	def test_marks_active_reminder_completed(self):
		"""Активное напоминание помечается выполненным с completed_at."""
		api = _make_api()
		session = _make_session()
		orm = _make_reminder_orm(is_completed=False, completed_at=None)

		with patch(_DB_PATH) as db:
			_patch_session(db, session)
			db.session_fetch_one = AsyncMock(return_value=orm)
			result = _run(api.complete_reminder(reminder_id=str(uuid4())))

		assert orm.is_completed is True
		assert orm.completed_at is not None
		assert isinstance(result, ReminderDetailSchema)
		session.commit.assert_awaited_once()

	def test_idempotent_preserves_original_completed_at(self):
		"""Повторный вызов не меняет исходное completed_at и не коммитит."""
		api = _make_api()
		session = _make_session()
		original = datetime(2026, 5, 1, 9, 0, tzinfo=timezone.utc)
		orm = _make_reminder_orm(is_completed=True, completed_at=original)

		with patch(_DB_PATH) as db:
			_patch_session(db, session)
			db.session_fetch_one = AsyncMock(return_value=orm)
			_run(api.complete_reminder(reminder_id=str(uuid4())))

		assert orm.completed_at == original
		session.commit.assert_not_awaited()

	def test_missing_reminder_raises_404(self):
		"""Отсутствующее напоминание → 404."""
		api = _make_api()
		session = _make_session()

		with patch(_DB_PATH) as db:
			_patch_session(db, session)
			db.session_fetch_one = AsyncMock(return_value=None)
			with pytest.raises(HTTPException) as exc_info:
				_run(api.complete_reminder(reminder_id=str(uuid4())))

		assert exc_info.value.status_code == 404


class TestUncompleteReminderEndpoint:
	"""Tests for ReminderAPI.uncomplete_reminder."""

	def test_clears_completed_state(self):
		"""Выполненное напоминание возвращается в активные (completed_at=None)."""
		api = _make_api()
		session = _make_session()
		orm = _make_reminder_orm(
			is_completed=True,
			completed_at=datetime(2026, 5, 1, 9, 0, tzinfo=timezone.utc),
		)

		with patch(_DB_PATH) as db:
			_patch_session(db, session)
			db.session_fetch_one = AsyncMock(return_value=orm)
			_run(api.uncomplete_reminder(reminder_id=str(uuid4())))

		assert orm.is_completed is False
		assert orm.completed_at is None
		session.commit.assert_awaited_once()

	def test_noop_when_already_active(self):
		"""Активное напоминание не меняется и не коммитится."""
		api = _make_api()
		session = _make_session()
		orm = _make_reminder_orm(is_completed=False, completed_at=None)

		with patch(_DB_PATH) as db:
			_patch_session(db, session)
			db.session_fetch_one = AsyncMock(return_value=orm)
			_run(api.uncomplete_reminder(reminder_id=str(uuid4())))

		assert orm.is_completed is False
		session.commit.assert_not_awaited()

	def test_missing_reminder_raises_404(self):
		"""Отсутствующее напоминание → 404."""
		api = _make_api()
		session = _make_session()

		with patch(_DB_PATH) as db:
			_patch_session(db, session)
			db.session_fetch_one = AsyncMock(return_value=None)
			with pytest.raises(HTTPException) as exc_info:
				_run(api.uncomplete_reminder(reminder_id=str(uuid4())))

		assert exc_info.value.status_code == 404


class TestDeleteReminderEndpoint:
	"""Tests for ReminderAPI.delete_reminder."""

	def test_deletes_owned_reminder(self):
		"""Удаляет напоминание текущего пользователя."""
		api = _make_api()
		session = _make_session()
		orm = _make_reminder_orm()

		with patch(_DB_PATH) as db:
			_patch_session(db, session)
			db.session_fetch_one = AsyncMock(return_value=orm)
			result = _run(api.delete_reminder(reminder_id=str(uuid4())))

		assert result is None
		session.delete.assert_awaited_once_with(orm)
		session.commit.assert_awaited_once()

	def test_missing_reminder_raises_404(self):
		"""Отсутствующее/чужое напоминание → 404, удаления нет."""
		api = _make_api()
		session = _make_session()

		with patch(_DB_PATH) as db:
			_patch_session(db, session)
			db.session_fetch_one = AsyncMock(return_value=None)
			with pytest.raises(HTTPException) as exc_info:
				_run(api.delete_reminder(reminder_id=str(uuid4())))

		assert exc_info.value.status_code == 404
		session.delete.assert_not_awaited()
