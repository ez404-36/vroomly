"""Tests for AuthService — аутентификация, login, logout, регистрация.

Ключевой root-cause-инвариант: ``authenticate`` возвращает ``User | None``
единообразно (нет ``HTTPException`` и нет различия «не найден» / «неверный пароль»).
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Coroutine, TypeVar
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from apps.accounts.api.schemas.mutators import RegistrationDataForm
from apps.accounts.services.auth import AuthService
from core.safety.token import Token, verify_password

T = TypeVar('T')

_REPO = 'apps.accounts.services.auth.UserRepository'
_DB = 'apps.accounts.services.auth.database'
_VERIFY = 'apps.accounts.services.auth.verify_password'
_CREATE_TOKEN = 'apps.accounts.services.auth.create_access_token'
_DECODE_CLAIMS = 'apps.accounts.services.auth.decode_token_claims'
_SESSION_MODEL = 'apps.accounts.services.auth.UserSession'


def _run(coro: Coroutine[Any, Any, T]) -> T:
	return asyncio.run(coro)


def _session_cm(session: Any) -> Any:
	cm = MagicMock()
	cm.__aenter__ = AsyncMock(return_value=session)
	cm.__aexit__ = AsyncMock(return_value=False)
	return cm


def _make_session() -> Any:
	session = MagicMock()
	session.add = MagicMock()
	session.commit = AsyncMock()
	session.refresh = AsyncMock()
	return session


def _repo_with_user(user: Any) -> Any:
	repo = MagicMock()
	repo.get_active_by_login_or_email = AsyncMock(return_value=user)
	return repo


class TestAuthenticate:
	def test_returns_none_when_user_not_found(self):
		"""Пользователь не найден → None (не исключение)."""
		with patch(_REPO, return_value=_repo_with_user(None)):
			result = _run(AuthService().authenticate('ghost', 'pwd'))
		assert result is None

	def test_returns_none_when_password_invalid(self):
		"""Пользователь найден, но пароль неверен → None (тот же сигнал)."""
		user = MagicMock(password_hash='hash')
		with (
			patch(_REPO, return_value=_repo_with_user(user)),
			patch(_VERIFY, return_value=False),
		):
			result = _run(AuthService().authenticate('user', 'wrong'))
		assert result is None

	def test_returns_user_on_success(self):
		user = MagicMock(password_hash='hash')
		with (
			patch(_REPO, return_value=_repo_with_user(user)),
			patch(_VERIFY, return_value=True),
		):
			result = _run(AuthService().authenticate('user', 'right'))
		assert result is user


class TestLogin:
	def test_returns_none_when_auth_fails(self):
		"""Неуспешная аутентификация → None, сессия не создаётся."""
		session = _make_session()
		with (
			patch(_REPO, return_value=_repo_with_user(None)),
			patch(f'{_DB}.get_async_session', return_value=_session_cm(session)),
		):
			result = _run(AuthService().login('ghost', 'pwd'))
		assert result is None
		session.add.assert_not_called()

	def test_issues_token_and_persists_session(self):
		"""Успех: выпускается токен, декодируются claims, создаётся UserSession, коммит."""
		session = _make_session()
		user = MagicMock(id=uuid4(), password_hash='hash')
		session_record = MagicMock()
		expires_at = datetime(2026, 6, 1, tzinfo=timezone.utc)

		with (
			patch(_REPO, return_value=_repo_with_user(user)),
			patch(_VERIFY, return_value=True),
			patch(_CREATE_TOKEN, return_value='jwt-token'),
			patch(_DECODE_CLAIMS, return_value=('jti-123', expires_at)),
			patch(f'{_DB}.get_async_session', return_value=_session_cm(session)),
			patch(_SESSION_MODEL, return_value=session_record) as session_model,
		):
			result = _run(AuthService().login('user', 'right'))

		assert isinstance(result, Token)
		assert result.access_token == 'jwt-token'
		assert result.token_type == 'bearer'
		session_model.assert_called_once_with(user_id=user.id, token_jti='jti-123', expires_at=expires_at)
		session.add.assert_called_once_with(session_record)
		session.commit.assert_awaited_once()


class TestRegister:
	def test_creates_user_with_hashed_password(self):
		session = _make_session()
		data = RegistrationDataForm(
			login='newuser',
			email='new@example.com',
			password='secret123',
			confirm_password='secret123',
		)

		with patch(f'{_DB}.get_async_session', return_value=_session_cm(session)):
			user = _run(AuthService().register(data))

		assert user.login == 'newuser'
		assert user.email == 'new@example.com'
		# Пароль захеширован (не хранится в открытом виде).
		assert user.password_hash != 'secret123'
		assert verify_password('secret123', user.password_hash) is True
		session.add.assert_called_once_with(user)
		session.commit.assert_awaited_once()


class TestLogout:
	def test_deletes_user_sessions(self):
		user_id = uuid4()
		execute = AsyncMock()
		with patch(f'{_DB}.execute', new=execute):
			_run(AuthService().logout(user_id))
		execute.assert_awaited_once()
