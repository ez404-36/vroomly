"""Tests for ReminderService — бизнес-логика напоминаний.

Покрывает проверки владения и инварианты (идемпотентные complete/uncomplete,
частичное обновление, удаление). Сессия и репозитории мокаются; реального
обращения к БД нет.
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Coroutine, TypeVar
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from apps.vehicles.api.reminder.schemas import CreateReminderSchema, UpdateReminderSchema
from apps.vehicles.services.reminder import ReminderService

T = TypeVar('T')

_DB = 'apps.vehicles.services.reminder.database'
_USER_VEHICLE_REPO = 'apps.vehicles.services.reminder.UserVehicleRepository'
_REMINDER_REPO = 'apps.vehicles.services.reminder.ReminderRepository'


def _run(coro: Coroutine[Any, Any, T]) -> T:
	return asyncio.run(coro)


def _make_session() -> Any:
	session = MagicMock()
	session.add = MagicMock()
	session.commit = AsyncMock()
	session.refresh = AsyncMock()
	session.delete = AsyncMock()
	return session


def _session_cm(session: Any) -> Any:
	cm = MagicMock()
	cm.__aenter__ = AsyncMock(return_value=session)
	cm.__aexit__ = AsyncMock(return_value=False)
	return cm


def _repo_returning(value: Any, method: str = 'get_owned') -> Any:
	repo = MagicMock()
	setattr(repo, method, AsyncMock(return_value=value))
	return repo


class TestReminderServiceCreate:
	def test_returns_none_when_vehicle_not_owned(self):
		"""ТС не принадлежит пользователю → None, ничего не добавляется."""
		session = _make_session()
		uv_repo = _repo_returning(None)

		with (
			patch(f'{_DB}.get_async_session', return_value=_session_cm(session)),
			patch(_USER_VEHICLE_REPO, return_value=uv_repo),
		):
			result = _run(
				ReminderService().create(uuid4(), uuid4(), CreateReminderSchema(title='Тест')),
			)

		assert result is None
		session.add.assert_not_called()
		session.commit.assert_not_called()

	def test_creates_reminder_for_owned_vehicle(self):
		"""ТС принадлежит пользователю → создаётся напоминание с корректными полями."""
		session = _make_session()
		user_id = uuid4()
		uv_id = uuid4()
		uv_repo = _repo_returning(MagicMock(id=uv_id))

		with (
			patch(f'{_DB}.get_async_session', return_value=_session_cm(session)),
			patch(_USER_VEHICLE_REPO, return_value=uv_repo),
		):
			result = _run(
				ReminderService().create(
					uv_id,
					user_id,
					CreateReminderSchema(title='Замена масла', is_all_day=True),
				),
			)

		session.add.assert_called_once()
		added = session.add.call_args.args[0]
		assert added.user_id == user_id
		assert added.user_vehicle_id == uv_id
		assert added.title == 'Замена масла'
		assert added.is_all_day is True
		assert added.is_completed is False
		assert added.completed_at is None
		session.commit.assert_awaited_once()
		assert result is added


class TestReminderServiceListForVehicle:
	def test_returns_none_when_not_owned(self):
		session = _make_session()
		uv_repo = _repo_returning(None)

		with (
			patch(f'{_DB}.get_async_session', return_value=_session_cm(session)),
			patch(_USER_VEHICLE_REPO, return_value=uv_repo),
		):
			result = _run(ReminderService().list_for_vehicle(uuid4(), uuid4()))

		assert result is None

	def test_returns_reminders_from_repository(self):
		session = _make_session()
		uv_id = uuid4()
		user_id = uuid4()
		reminders = [MagicMock(), MagicMock()]
		uv_repo = _repo_returning(MagicMock())
		rem_repo = MagicMock()
		rem_repo.list_for_vehicle = AsyncMock(return_value=reminders)

		with (
			patch(f'{_DB}.get_async_session', return_value=_session_cm(session)),
			patch(_USER_VEHICLE_REPO, return_value=uv_repo),
			patch(_REMINDER_REPO, return_value=rem_repo),
		):
			result = _run(ReminderService().list_for_vehicle(uv_id, user_id, is_completed=True))

		assert result == reminders
		rem_repo.list_for_vehicle.assert_awaited_once_with(uv_id, user_id, True)


class TestReminderServiceUpdate:
	def test_returns_none_when_missing(self):
		session = _make_session()
		rem_repo = _repo_returning(None)

		with (
			patch(f'{_DB}.get_async_session', return_value=_session_cm(session)),
			patch(_REMINDER_REPO, return_value=rem_repo),
		):
			result = _run(
				ReminderService().update(uuid4(), uuid4(), UpdateReminderSchema(title='Новое')),
			)

		assert result is None
		session.commit.assert_not_called()

	def test_applies_only_provided_fields(self):
		session = _make_session()
		reminder = MagicMock(title='Старое', description='Старое описание')
		rem_repo = _repo_returning(reminder)

		with (
			patch(f'{_DB}.get_async_session', return_value=_session_cm(session)),
			patch(_REMINDER_REPO, return_value=rem_repo),
		):
			_run(ReminderService().update(uuid4(), uuid4(), UpdateReminderSchema(title='Новое')))

		assert reminder.title == 'Новое'
		assert reminder.description == 'Старое описание'
		session.commit.assert_awaited_once()

	def test_explicit_none_clears_field(self):
		session = _make_session()
		reminder = MagicMock(due_at=datetime(2026, 6, 1, tzinfo=timezone.utc))
		rem_repo = _repo_returning(reminder)

		with (
			patch(f'{_DB}.get_async_session', return_value=_session_cm(session)),
			patch(_REMINDER_REPO, return_value=rem_repo),
		):
			_run(ReminderService().update(uuid4(), uuid4(), UpdateReminderSchema(due_at=None)))

		assert reminder.due_at is None


class TestReminderServiceComplete:
	def test_marks_active_completed(self):
		session = _make_session()
		reminder = MagicMock(is_completed=False, completed_at=None)
		rem_repo = _repo_returning(reminder)

		with (
			patch(f'{_DB}.get_async_session', return_value=_session_cm(session)),
			patch(_REMINDER_REPO, return_value=rem_repo),
		):
			_run(ReminderService().complete(uuid4(), uuid4()))

		assert reminder.is_completed is True
		assert reminder.completed_at is not None
		session.commit.assert_awaited_once()

	def test_idempotent_preserves_completed_at(self):
		"""Повторный complete не меняет исходное completed_at и не коммитит."""
		session = _make_session()
		original = datetime(2026, 5, 1, 9, 0, tzinfo=timezone.utc)
		reminder = MagicMock(is_completed=True, completed_at=original)
		rem_repo = _repo_returning(reminder)

		with (
			patch(f'{_DB}.get_async_session', return_value=_session_cm(session)),
			patch(_REMINDER_REPO, return_value=rem_repo),
		):
			_run(ReminderService().complete(uuid4(), uuid4()))

		assert reminder.completed_at == original
		session.commit.assert_not_called()

	def test_missing_returns_none(self):
		session = _make_session()
		rem_repo = _repo_returning(None)
		with (
			patch(f'{_DB}.get_async_session', return_value=_session_cm(session)),
			patch(_REMINDER_REPO, return_value=rem_repo),
		):
			result = _run(ReminderService().complete(uuid4(), uuid4()))
		assert result is None


class TestReminderServiceUncomplete:
	def test_clears_completed_state(self):
		session = _make_session()
		reminder = MagicMock(
			is_completed=True,
			completed_at=datetime(2026, 5, 1, 9, 0, tzinfo=timezone.utc),
		)
		rem_repo = _repo_returning(reminder)

		with (
			patch(f'{_DB}.get_async_session', return_value=_session_cm(session)),
			patch(_REMINDER_REPO, return_value=rem_repo),
		):
			_run(ReminderService().uncomplete(uuid4(), uuid4()))

		assert reminder.is_completed is False
		assert reminder.completed_at is None
		session.commit.assert_awaited_once()

	def test_noop_when_already_active(self):
		session = _make_session()
		reminder = MagicMock(is_completed=False, completed_at=None)
		rem_repo = _repo_returning(reminder)

		with (
			patch(f'{_DB}.get_async_session', return_value=_session_cm(session)),
			patch(_REMINDER_REPO, return_value=rem_repo),
		):
			_run(ReminderService().uncomplete(uuid4(), uuid4()))

		assert reminder.is_completed is False
		session.commit.assert_not_called()


class TestReminderServiceDelete:
	def test_deletes_owned(self):
		session = _make_session()
		reminder = MagicMock()
		rem_repo = _repo_returning(reminder)

		with (
			patch(f'{_DB}.get_async_session', return_value=_session_cm(session)),
			patch(_REMINDER_REPO, return_value=rem_repo),
		):
			result = _run(ReminderService().delete(uuid4(), uuid4()))

		assert result is True
		session.delete.assert_awaited_once_with(reminder)
		session.commit.assert_awaited_once()

	def test_returns_false_when_missing(self):
		session = _make_session()
		rem_repo = _repo_returning(None)

		with (
			patch(f'{_DB}.get_async_session', return_value=_session_cm(session)),
			patch(_REMINDER_REPO, return_value=rem_repo),
		):
			result = _run(ReminderService().delete(uuid4(), uuid4()))

		assert result is False
		session.delete.assert_not_called()
