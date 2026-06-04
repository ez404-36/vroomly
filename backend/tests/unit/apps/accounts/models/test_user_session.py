"""Tests for UserSession model.

После выноса парсинга токена в ``core.safety.token.decode_token_claims`` модель
стала простым ORM-объектом: проверяем только конфигурацию полей и присвоение
готовых ``token_jti``/``expires_at`` через конструктор.
"""

from datetime import datetime, timezone
from uuid import UUID

from apps.accounts.models.user_session import UserSession


class TestUserSessionConstruction:
	"""Модель принимает готовые jti + expires_at в простом конструкторе."""

	def test_assigns_given_claims(self) -> None:
		user_id = UUID('62368046-3c26-4779-8f2d-ed668abb891f')
		expires_at = datetime(2026, 6, 1, 12, 0, tzinfo=timezone.utc)

		session = UserSession(user_id=user_id, token_jti='jti-123', expires_at=expires_at)

		assert session.user_id == user_id
		assert session.token_jti == 'jti-123'
		assert session.expires_at == expires_at


class TestUserSessionFields:
	"""Tests for UserSession field configurations."""

	def test_session_has_user_id_field(self) -> None:
		"""Test that UserSession has user_id field (from FK mixin)."""
		assert hasattr(UserSession, 'user_id')

	def test_session_has_token_jti(self) -> None:
		"""Test that UserSession has token_jti field."""
		assert hasattr(UserSession, 'token_jti')

	def test_session_has_created_at(self) -> None:
		"""Test that UserSession has created_at field."""
		assert hasattr(UserSession, 'created_at')

	def test_session_has_expires_at(self) -> None:
		"""Test that UserSession has expires_at field."""
		assert hasattr(UserSession, 'expires_at')

	def test_token_jti_is_unique(self) -> None:
		"""Test that token_jti column is configured as unique."""
		token_jti_col = UserSession.__table__.c.token_jti
		assert token_jti_col.unique is True
