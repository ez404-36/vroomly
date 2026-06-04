"""Tests for ProfileService — обновление профиля пользователя."""

import asyncio
from typing import Any, Coroutine, TypeVar
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from apps.accounts.services.profile import ProfileService
from common.schemas.models import UpdateUserProfile

T = TypeVar('T')

_REPO = 'apps.accounts.services.profile.UserRepository'
_DB = 'apps.accounts.services.profile.database'


def _run(coro: Coroutine[Any, Any, T]) -> T:
	return asyncio.run(coro)


def _session_cm(session: Any) -> Any:
	cm = MagicMock()
	cm.__aenter__ = AsyncMock(return_value=session)
	cm.__aexit__ = AsyncMock(return_value=False)
	return cm


def _make_session() -> Any:
	session = MagicMock()
	session.commit = AsyncMock()
	session.refresh = AsyncMock()
	return session


def _repo_with_user(user: Any) -> Any:
	repo = MagicMock()
	repo.get_by_id = AsyncMock(return_value=user)
	return repo


class TestProfileServiceUpdate:
	def test_returns_none_when_user_missing(self):
		"""Пользователь не найден → None, без коммита."""
		session = _make_session()
		with (
			patch(_REPO, return_value=_repo_with_user(None)),
			patch(f'{_DB}.get_async_session', return_value=_session_cm(session)),
		):
			result = _run(ProfileService().update(uuid4(), UpdateUserProfile(name='Иван')))
		assert result is None
		session.commit.assert_not_called()

	def test_applies_only_provided_fields(self):
		"""Применяются только переданные поля (exclude_unset)."""
		session = _make_session()
		user = MagicMock(surname='Прежняя')
		user.name = 'Старое'  # name= в MagicMock(...) — служебный kwarg, задаём явно
		with (
			patch(_REPO, return_value=_repo_with_user(user)),
			patch(f'{_DB}.get_async_session', return_value=_session_cm(session)),
		):
			result = _run(ProfileService().update(uuid4(), UpdateUserProfile(name='Иван')))

		assert user.name == 'Иван'
		assert user.surname == 'Прежняя'
		session.commit.assert_awaited_once()
		assert result is user
