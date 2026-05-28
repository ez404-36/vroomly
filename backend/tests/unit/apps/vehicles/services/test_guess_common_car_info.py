"""Tests for GuessCommonCarInfo service fuzzy lookup logic."""

import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Coroutine, TypeVar
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest

from apps.vehicles.models.vehicle.vehicle_brand import VehicleBrand
from apps.vehicles.models.vehicle.vehicle_series import VehicleSeries
from apps.vehicles.services.guess_common_car_info import (
	MIN_FUZZY_QUERY_LENGTH,
	TRIGRAM_AMBIGUITY_EPS,
	TRIGRAM_THRESHOLD,
	GuessCommonCarInfo,
	GuessCommonCarInfoError,
)

T = TypeVar('T')


def _run(coro: Coroutine[Any, Any, T]) -> T:
	"""Запускает корутину в свежем event loop (отказ от pytest-asyncio)."""
	return asyncio.run(coro)


def _make_brand(name: str) -> Any:
	"""Возвращает duck-typed заглушку VehicleBrand. ORM-state не нужен — сервис обращается только к атрибутам."""
	stub = MagicMock(spec=VehicleBrand)
	stub.id = uuid4()
	stub.name = name
	return stub


def _make_series(name: str, brand_id: UUID | None = None) -> Any:
	"""Возвращает duck-typed заглушку VehicleSeries."""
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


class TestFuzzyLookupExactMatch:
	"""Если точное совпадение найдено, trigram-запрос вообще не выполняется."""

	def test_exact_match_returns_immediately(self) -> None:
		brand = _make_brand('HYUNDAI')
		with (
			patch(
				'apps.vehicles.services.guess_common_car_info.database.fetch_one',
				new=AsyncMock(return_value=brand),
			) as fetch_one_mock,
			patch(
				'apps.vehicles.services.guess_common_car_info.database.get_async_session',
			) as session_mock,
		):
			result = _run(GuessCommonCarInfo._fuzzy_lookup(VehicleBrand, 'HYUNDAI'))

		assert result is brand
		fetch_one_mock.assert_awaited_once()
		session_mock.assert_not_called()


class TestFuzzyLookupSingleCandidate:
	"""Один кандидат выше порога — возвращается без дополнительных проверок."""

	def test_single_candidate_returned(self) -> None:
		series = _make_series('TUCSON')
		with (
			patch(
				'apps.vehicles.services.guess_common_car_info.database.fetch_one',
				new=AsyncMock(return_value=None),
			),
			patch(
				'apps.vehicles.services.guess_common_car_info.database.get_async_session',
				return_value=_fake_session_cm([(series, 0.72)]),
			),
		):
			result = _run(GuessCommonCarInfo._fuzzy_lookup(VehicleSeries, 'TUXON'))

		assert result is series


class TestFuzzyLookupTwoCandidates:
	"""При двух кандидатах учитывается разница score между top-1 и top-2."""

	def test_clear_winner_returned(self) -> None:
		winner = _make_series('TUCSON')
		runner_up = _make_series('TUSCANY')
		gap = TRIGRAM_AMBIGUITY_EPS + 0.05
		rows = [(winner, 0.80), (runner_up, 0.80 - gap)]
		with (
			patch(
				'apps.vehicles.services.guess_common_car_info.database.fetch_one',
				new=AsyncMock(return_value=None),
			),
			patch(
				'apps.vehicles.services.guess_common_car_info.database.get_async_session',
				return_value=_fake_session_cm(rows),
			),
		):
			result = _run(GuessCommonCarInfo._fuzzy_lookup(VehicleSeries, 'TUXON'))

		assert result is winner

	def test_ambiguity_raises(self) -> None:
		first = _make_series('TUCSON')
		second = _make_series('TUSCANY')
		gap = TRIGRAM_AMBIGUITY_EPS / 2
		rows = [(first, 0.70), (second, 0.70 - gap)]
		with (
			patch(
				'apps.vehicles.services.guess_common_car_info.database.fetch_one',
				new=AsyncMock(return_value=None),
			),
			patch(
				'apps.vehicles.services.guess_common_car_info.database.get_async_session',
				return_value=_fake_session_cm(rows),
			),
		):
			with pytest.raises(GuessCommonCarInfoError) as excinfo:
				_run(GuessCommonCarInfo._fuzzy_lookup(VehicleSeries, 'TUXON'))

		message = str(excinfo.value)
		assert 'TUCSON' in message
		assert 'TUSCANY' in message
		assert 'TUXON' in message


class TestFuzzyLookupZeroCandidates:
	"""Если fuzzy-поиск ничего не вернул, метод возвращает None."""

	def test_no_candidates_returns_none(self) -> None:
		with (
			patch(
				'apps.vehicles.services.guess_common_car_info.database.fetch_one',
				new=AsyncMock(return_value=None),
			),
			patch(
				'apps.vehicles.services.guess_common_car_info.database.get_async_session',
				return_value=_fake_session_cm([]),
			),
		):
			result = _run(GuessCommonCarInfo._fuzzy_lookup(VehicleBrand, 'НЕТНИГДЕ'))

		assert result is None


class TestFuzzyLookupShortQuery:
	"""Слишком короткие запросы не идут в trigram (защита от ложных совпадений)."""

	def test_short_query_skips_trigram(self) -> None:
		short_query = 'X' * (MIN_FUZZY_QUERY_LENGTH - 1)
		with (
			patch(
				'apps.vehicles.services.guess_common_car_info.database.fetch_one',
				new=AsyncMock(return_value=None),
			) as fetch_one_mock,
			patch(
				'apps.vehicles.services.guess_common_car_info.database.get_async_session',
			) as session_mock,
		):
			result = _run(GuessCommonCarInfo._fuzzy_lookup(VehicleBrand, short_query))

		assert result is None
		fetch_one_mock.assert_awaited_once()
		session_mock.assert_not_called()

	def test_whitespace_only_query_skips_trigram(self) -> None:
		with (
			patch(
				'apps.vehicles.services.guess_common_car_info.database.fetch_one',
				new=AsyncMock(return_value=None),
			),
			patch(
				'apps.vehicles.services.guess_common_car_info.database.get_async_session',
			) as session_mock,
		):
			result = _run(GuessCommonCarInfo._fuzzy_lookup(VehicleBrand, '   '))

		assert result is None
		session_mock.assert_not_called()


class TestGuessBrandSeries:
	"""``_guess_brand`` и ``_guess_series`` делегируют в ``_fuzzy_lookup``."""

	def test_guess_brand_delegates(self) -> None:
		brand = _make_brand('HYUNDAI')
		with patch.object(GuessCommonCarInfo, '_fuzzy_lookup', new=AsyncMock(return_value=brand)) as lookup_mock:
			result = _run(GuessCommonCarInfo._guess_brand('HYUNDAI'))

		assert result is brand
		lookup_mock.assert_awaited_once_with(VehicleBrand, 'HYUNDAI')

	def test_guess_series_passes_brand_filter(self) -> None:
		series = _make_series('TUCSON')
		brand_id = uuid4()
		with patch.object(GuessCommonCarInfo, '_fuzzy_lookup', new=AsyncMock(return_value=series)) as lookup_mock:
			result = _run(GuessCommonCarInfo._guess_series(brand_id, 'TUXON'))

		assert result is series
		assert lookup_mock.await_count == 1
		args, kwargs = lookup_mock.call_args
		assert args[0] is VehicleSeries
		assert args[1] == 'TUXON'
		assert 'extra_where' in kwargs
		assert kwargs['extra_where'] is not None


class TestTuxonScenario:
	"""Сценарий из багрепорта: 'ТУКСОН' переведён как 'TUXON' — должен найти 'TUCSON'."""

	def test_tuxon_finds_tucson_via_trigram(self) -> None:
		tucson = _make_series('TUCSON')
		brand_id = uuid4()
		with (
			patch(
				'apps.vehicles.services.guess_common_car_info.database.fetch_one',
				new=AsyncMock(return_value=None),
			),
			patch(
				'apps.vehicles.services.guess_common_car_info.database.get_async_session',
				return_value=_fake_session_cm([(tucson, TRIGRAM_THRESHOLD + 0.05)]),
			),
		):
			result = _run(GuessCommonCarInfo._guess_series(brand_id, 'TUXON'))

		assert result is tucson
		assert result is not None
		assert result.name == 'TUCSON'
