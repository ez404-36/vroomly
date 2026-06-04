"""Tests for core.safety.token — хеширование паролей и выпуск JWT.

После унификации хеширование живёт ТОЛЬКО здесь (модель ``User`` больше не
хеширует пароли). Покрываем round-trip ``get_password_hash``/``verify_password``
и фиксированный cost-фактор ``BCRYPT_COST``.
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
import pytest

from core.safety.token import (
	ACCESS_TOKEN_EXPIRE_MINUTES,
	ALGORITHM,
	BCRYPT_COST,
	SECRET_KEY,
	create_access_token,
	decode_token_claims,
	get_password_hash,
	verify_password,
)


class TestPasswordHashing:
	def test_hash_differs_from_plain(self) -> None:
		"""Хеш не равен исходному паролю."""
		hashed = get_password_hash('secret123')
		assert hashed != 'secret123'

	def test_verify_accepts_correct_password(self) -> None:
		hashed = get_password_hash('secret123')
		assert verify_password('secret123', hashed) is True

	def test_verify_rejects_wrong_password(self) -> None:
		hashed = get_password_hash('secret123')
		assert verify_password('wrong', hashed) is False

	def test_hash_uses_configured_cost_factor(self) -> None:
		"""Хеш использует именно ``BCRYPT_COST`` rounds (единый cost-фактор)."""
		hashed = get_password_hash('secret123')
		rounds = bcrypt.gensalt(rounds=BCRYPT_COST).decode('utf-8').split('$')[2]
		assert hashed.split('$')[2] == rounds

	def test_two_hashes_of_same_password_differ(self) -> None:
		"""Соль случайна → два хеша одного пароля различаются, но оба валидны."""
		first = get_password_hash('secret123')
		second = get_password_hash('secret123')
		assert first != second
		assert verify_password('secret123', first) is True
		assert verify_password('secret123', second) is True


class TestCreateAccessToken:
	def test_token_contains_jti_and_exp(self) -> None:
		token = create_access_token(data={'sub': 'user-id'})
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		assert payload['sub'] == 'user-id'
		assert 'jti' in payload
		assert 'exp' in payload

	def test_each_token_has_unique_jti(self) -> None:
		first = jwt.decode(create_access_token(data={'sub': 'u'}), SECRET_KEY, algorithms=[ALGORITHM])
		second = jwt.decode(create_access_token(data={'sub': 'u'}), SECRET_KEY, algorithms=[ALGORITHM])
		assert first['jti'] != second['jti']


class TestDecodeTokenClaims:
	"""Парсинг ``jti`` и времени истечения из JWT (без проверки подписи)."""

	def test_extracts_jti_and_exp(self) -> None:
		exp_timestamp = int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())
		token = jwt.encode(
			{'sub': 'user', 'jti': 'jti-abc', 'exp': exp_timestamp},
			SECRET_KEY,
			algorithm=ALGORITHM,
		)

		jti, expires_at = decode_token_claims(token)

		assert jti == 'jti-abc'
		assert expires_at.timestamp() == pytest.approx(exp_timestamp, rel=1)

	def test_missing_jti_yields_empty_string(self) -> None:
		exp_timestamp = int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())
		token = jwt.encode({'sub': 'user', 'exp': exp_timestamp}, SECRET_KEY, algorithm=ALGORITHM)

		jti, expires_at = decode_token_claims(token)

		assert jti == ''
		assert expires_at.timestamp() == pytest.approx(exp_timestamp, rel=1)

	def test_missing_exp_uses_default_expiry(self) -> None:
		token = jwt.encode({'sub': 'user', 'jti': 'jti-xyz'}, SECRET_KEY, algorithm=ALGORITHM)

		jti, expires_at = decode_token_claims(token)

		assert jti == 'jti-xyz'
		expected = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
		assert expires_at.timestamp() == pytest.approx(expected.timestamp(), rel=1)
		assert expires_at.tzinfo is not None
