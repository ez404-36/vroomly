"""Tests for repository ownership lookups.

Ключевое поведение SRP/root-cause: методы поиска фильтруют по ``user_id`` и
возвращают объект или ``None``, не бросая ``HTTPException`` (HTTP-семантика
остаётся в слое эндпоинтов).
"""

import asyncio
from typing import Any, Coroutine, TypeVar
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from apps.vehicles.repositories.reminder import ReminderRepository
from apps.vehicles.repositories.user_vehicle import UserVehicleRepository

T = TypeVar('T')


def _run(coro: Coroutine[Any, Any, T]) -> T:
	return asyncio.run(coro)


class TestUserVehicleRepositoryOwnership:
	def test_get_owned_returns_none_without_raising(self):
		"""Нет записи владельца — возвращается None, исключение не бросается."""
		repo = UserVehicleRepository()
		with patch.object(repo, '_fetch_one', new=AsyncMock(return_value=None)) as fetch:
			result = _run(repo.get_owned(uuid4(), uuid4()))
		assert result is None
		fetch.assert_awaited_once()

	def test_get_owned_returns_entity(self):
		"""Запись найдена — возвращается она же."""
		repo = UserVehicleRepository()
		entity = object()
		with patch.object(repo, '_fetch_one', new=AsyncMock(return_value=entity)):
			result = _run(repo.get_owned(uuid4(), uuid4()))
		assert result is entity

	def test_get_owned_query_filters_by_user_and_id(self):
		"""Запрос ограничивает выборку и по id ТС, и по user_id (проверка владения в SQL)."""
		repo = UserVehicleRepository()
		uv_id = uuid4()
		user_id = uuid4()
		captured: dict[str, Any] = {}

		async def _capture(query: Any) -> None:
			captured['sql'] = str(query.compile(compile_kwargs={'literal_binds': True}))

		with patch.object(repo, '_fetch_one', new=_capture):
			_run(repo.get_owned(uv_id, user_id))

		sql = captured['sql']
		# В скомпилированном SQL UUID рендерится без дефисов (hex).
		assert uv_id.hex in sql
		assert user_id.hex in sql


class TestReminderRepositoryOwnership:
	def test_get_owned_returns_none_without_raising(self):
		repo = ReminderRepository()
		with patch.object(repo, '_fetch_one', new=AsyncMock(return_value=None)):
			result = _run(repo.get_owned(uuid4(), uuid4()))
		assert result is None

	def test_list_for_vehicle_applies_completed_filter(self):
		"""При заданном is_completed запрос содержит фильтр по статусу выполнения."""
		repo = ReminderRepository()
		captured: dict[str, Any] = {}

		async def _capture(query: Any) -> list[Any]:
			captured['sql'] = str(query.compile(compile_kwargs={'literal_binds': True}))
			return []

		with patch.object(repo, '_fetch_all', new=_capture):
			_run(repo.list_for_vehicle(uuid4(), uuid4(), is_completed=True))

		assert 'is_completed' in captured['sql']
