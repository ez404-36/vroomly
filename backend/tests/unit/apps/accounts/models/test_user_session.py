"""Tests for UserSession model."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
import pytest

from apps.accounts.models.user_session import UserSession
from core.safety.token import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY


class TestUserSessionCreateFromToken:
	"""Tests for UserSession.create_from_token classmethod."""

	def test_create_from_token_with_full_token(self) -> None:
		"""Test creating session from valid token with jti and exp claims."""
		user_id = UUID('62368046-3c26-4779-8f2d-ed668abb891f')
		exp_timestamp = int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())
		jti = 'test-jti-12345'

		token_payload = {
			'sub': str(user_id),
			'exp': exp_timestamp,
			'jti': jti,
		}
		token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)

		session = UserSession.create_from_token(user_id=user_id, token=token)

		assert session.user_id == user_id
		assert session.token_jti == jti
		assert session.expires_at.timestamp() == pytest.approx(exp_timestamp, rel=1)

	def test_create_from_token_without_jti(self) -> None:
		"""Test creating session from token without jti claim."""
		user_id = UUID('62368046-3c26-4779-8f2d-ed668abb891f')
		exp_timestamp = int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())

		token_payload = {
			'sub': str(user_id),
			'exp': exp_timestamp,
		}
		token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)

		session = UserSession.create_from_token(user_id=user_id, token=token)

		assert session.user_id == user_id
		assert session.token_jti == ''
		assert session.expires_at.timestamp() == pytest.approx(exp_timestamp, rel=1)

	def test_create_from_token_without_exp(self) -> None:
		"""Test creating session from token without exp claim uses default expiration."""
		user_id = UUID('62368046-3c26-4779-8f2d-ed668abb891f')

		token_payload = {
			'sub': str(user_id),
			'jti': 'test-jti',
		}
		token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)

		session = UserSession.create_from_token(user_id=user_id, token=token)

		assert session.user_id == user_id
		assert session.token_jti == 'test-jti'
		expected_exp = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
		assert session.expires_at.timestamp() == pytest.approx(expected_exp.timestamp(), rel=1)


class TestUserSessionDefaultExpires:
	"""Tests for UserSession._default_expires staticmethod."""

	def test_default_expires_timedelta(self) -> None:
		"""Test that default expiration is ACCESS_TOKEN_EXPIRE_MINUTES from now."""
		before = datetime.now(timezone.utc)
		expires = UserSession._default_expires()
		after = datetime.now(timezone.utc)

		expected_min = before + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
		expected_max = after + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

		assert expected_min.timestamp() <= expires.timestamp() <= expected_max.timestamp()


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
