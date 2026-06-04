"""Tests for UserRepository — доступ к данным пользователей.

Root-cause-инвариант: поиск возвращает ``None`` без исключения; выборка
по login/email фильтрует не удалённых пользователей.
"""

import asyncio
from typing import Any, Coroutine, TypeVar
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from apps.accounts.repositories.user import UserRepository

T = TypeVar('T')


def _run(coro: Coroutine[Any, Any, T]) -> T:
	return asyncio.run(coro)


class TestUserRepository:
	def test_get_active_returns_none_without_raising(self):
		repo = UserRepository()
		with patch.object(repo, '_fetch_one', new=AsyncMock(return_value=None)):
			result = _run(repo.get_active_by_login_or_email('ghost'))
		assert result is None

	def test_get_active_query_matches_login_or_email_and_excludes_deleted(self):
		"""Запрос ищет по login ИЛИ email и исключает удалённых."""
		repo = UserRepository()
		captured: dict[str, Any] = {}

		async def _capture(query: Any) -> None:
			captured['sql'] = str(query.compile(compile_kwargs={'literal_binds': True}))

		with patch.object(repo, '_fetch_one', new=_capture):
			_run(repo.get_active_by_login_or_email('john'))

		sql = captured['sql'].lower()
		assert 'login' in sql
		assert 'email' in sql
		assert 'deleted' in sql

	def test_get_by_id_returns_entity(self):
		repo = UserRepository()
		entity = object()
		with patch.object(repo, '_fetch_one', new=AsyncMock(return_value=entity)):
			result = _run(repo.get_by_id(uuid4()))
		assert result is entity
