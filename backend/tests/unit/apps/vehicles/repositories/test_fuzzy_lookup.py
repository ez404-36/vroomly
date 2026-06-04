"""Tests for fuzzy_lookup repository — trigram-подбор по полю name."""

import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Coroutine, TypeVar
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest

from apps.vehicles.models.vehicle.vehicle_brand import VehicleBrand
from apps.vehicles.models.vehicle.vehicle_series import VehicleSeries
from apps.vehicles.repositories.fuzzy_lookup import (
	MIN_FUZZY_QUERY_LENGTH,
	TRIGRAM_AMBIGUITY_EPS,
	GuessCommonCarInfoError,
	fuzzy_lookup,
)

T = TypeVar('T')

_DB = 'apps.vehicles.repositories.fuzzy_lookup.database'


def _run(coro: Coroutine[Any, Any, T]) -> T:
	return asyncio.run(coro)


def _make_brand(name: str) -> Any:
	stub = MagicMock(spec=VehicleBrand)
	stub.id = uuid4()
	stub.name = name
	return stub


def _make_series(name: str, brand_id: UUID | None = None) -> Any:
	stub = MagicMock(spec=VehicleSeries)
	stub.id = uuid4()
	stub.name = name
	stub.brand_id = brand_id or uuid4()
	return stub


@asynccontextmanager
async def _fake_session_cm(rows: list[tuple[Any, float]]) -> AsyncIterator[MagicMock]:
	"""Имитирует ``database.get_async_session()`` async context manager."""
	session = MagicMock()
	result = MagicMock()
	result.all = MagicMock(return_value=rows)
	session.execute = AsyncMock(return_value=result)
	yield session


class TestExactMatch:
	def test_exact_match_returns_immediately(self) -> None:
		"""Точное совпадение — trigram-запрос не выполняется."""
		brand = _make_brand('HYUNDAI')
		with (
			patch(f'{_DB}.fetch_one', new=AsyncMock(return_value=brand)) as fetch_one_mock,
			patch(f'{_DB}.get_async_session') as session_mock,
		):
			result = _run(fuzzy_lookup(VehicleBrand, 'HYUNDAI'))

		assert result is brand
		fetch_one_mock.assert_awaited_once()
		session_mock.assert_not_called()


class TestSingleCandidate:
	def test_single_candidate_returned(self) -> None:
		series = _make_series('TUCSON')
		with (
			patch(f'{_DB}.fetch_one', new=AsyncMock(return_value=None)),
			patch(f'{_DB}.get_async_session', return_value=_fake_session_cm([(series, 0.72)])),
		):
			result = _run(fuzzy_lookup(VehicleSeries, 'TUXON'))

		assert result is series


class TestTwoCandidates:
	def test_clear_winner_returned(self) -> None:
		winner = _make_series('TUCSON')
		runner_up = _make_series('TUSCANY')
		gap = TRIGRAM_AMBIGUITY_EPS + 0.05
		rows = [(winner, 0.80), (runner_up, 0.80 - gap)]
		with (
			patch(f'{_DB}.fetch_one', new=AsyncMock(return_value=None)),
			patch(f'{_DB}.get_async_session', return_value=_fake_session_cm(rows)),
		):
			result = _run(fuzzy_lookup(VehicleSeries, 'TUXON'))

		assert result is winner

	def test_ambiguity_raises(self) -> None:
		first = _make_series('TUCSON')
		second = _make_series('TUSCANY')
		gap = TRIGRAM_AMBIGUITY_EPS / 2
		rows = [(first, 0.70), (second, 0.70 - gap)]
		with (
			patch(f'{_DB}.fetch_one', new=AsyncMock(return_value=None)),
			patch(f'{_DB}.get_async_session', return_value=_fake_session_cm(rows)),
		):
			with pytest.raises(GuessCommonCarInfoError) as excinfo:
				_run(fuzzy_lookup(VehicleSeries, 'TUXON'))

		message = str(excinfo.value)
		assert 'TUCSON' in message
		assert 'TUSCANY' in message
		assert 'TUXON' in message


class TestZeroCandidates:
	def test_no_candidates_returns_none(self) -> None:
		with (
			patch(f'{_DB}.fetch_one', new=AsyncMock(return_value=None)),
			patch(f'{_DB}.get_async_session', return_value=_fake_session_cm([])),
		):
			result = _run(fuzzy_lookup(VehicleBrand, 'НЕТНИГДЕ'))

		assert result is None


class TestShortQuery:
	def test_short_query_skips_trigram(self) -> None:
		short_query = 'X' * (MIN_FUZZY_QUERY_LENGTH - 1)
		with (
			patch(f'{_DB}.fetch_one', new=AsyncMock(return_value=None)) as fetch_one_mock,
			patch(f'{_DB}.get_async_session') as session_mock,
		):
			result = _run(fuzzy_lookup(VehicleBrand, short_query))

		assert result is None
		fetch_one_mock.assert_awaited_once()
		session_mock.assert_not_called()

	def test_whitespace_only_query_skips_trigram(self) -> None:
		with (
			patch(f'{_DB}.fetch_one', new=AsyncMock(return_value=None)),
			patch(f'{_DB}.get_async_session') as session_mock,
		):
			result = _run(fuzzy_lookup(VehicleBrand, '   '))

		assert result is None
		session_mock.assert_not_called()
