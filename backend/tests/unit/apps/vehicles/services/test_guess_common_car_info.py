"""Tests for GuessCommonCarInfo service fuzzy lookup logic."""

import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Coroutine, TypeVar
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest

from apps.vehicles.models.car.car_body import CarBody
from apps.vehicles.models.car.car_transmission import CarTransmission
from apps.vehicles.models.car.car_trim import CarTrim
from apps.vehicles.models.car.enums import CarBodyType, CarDriveType
from apps.vehicles.models.vehicle.enums import VehicleEngineType, VehicleTransmissionType
from apps.vehicles.models.vehicle.vehicle_brand import VehicleBrand
from apps.vehicles.models.vehicle.vehicle_engine import VehicleEngine
from apps.vehicles.models.vehicle.vehicle_generation import VehicleGeneration
from apps.vehicles.models.vehicle.vehicle_series import VehicleSeries
from apps.vehicles.services.guess_common_car_info import (
	MIN_FUZZY_QUERY_LENGTH,
	TRIGRAM_AMBIGUITY_EPS,
	TRIGRAM_THRESHOLD,
	GuessCommonCarInfo,
	GuessCommonCarInfoError,
	_drive_type_label,
	_engine_type_label,
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


def _make_generation(name: str) -> Any:
	stub = MagicMock(spec=VehicleGeneration)
	stub.id = uuid4()
	stub.name = name
	return stub


def _make_engine(name: str, volume: int, power: int, engine_type: VehicleEngineType, torque: int | None) -> Any:
	stub = MagicMock(spec=VehicleEngine)
	stub.id = uuid4()
	stub.name = name
	stub.volume = volume
	stub.power = power
	stub.type = engine_type
	stub.torque = torque
	return stub


def _make_transmission(
	name: str,
	transmission_type: VehicleTransmissionType,
	gears: int,
	drive_types: list[CarDriveType],
) -> Any:
	stub = MagicMock(spec=CarTransmission)
	stub.id = uuid4()
	stub.name = name
	stub.type = transmission_type
	stub.gears = gears
	stub.drive_types = drive_types
	return stub


def _make_body(body_type: CarBodyType) -> Any:
	stub = MagicMock(spec=CarBody)
	stub.id = uuid4()
	stub.type = body_type
	return stub


def _make_trim(name: str, generation: Any, engine: Any, transmission: Any, body: Any) -> Any:
	stub = MagicMock(spec=CarTrim)
	stub.id = uuid4()
	stub.name = name
	stub.generation = generation
	stub.engine = engine
	stub.transmission = transmission
	stub.body = body
	return stub


class TestSerializeTrim:
	"""``_serialize_trim`` собирает расширенные данные о комплектации."""

	def test_full_trim(self) -> None:
		generation = _make_generation('III')
		engine = _make_engine('CWVA', 1600, 110, VehicleEngineType.PETROL | VehicleEngineType.ATMOSPHERIC, 155)
		transmission = _make_transmission('0AM', VehicleTransmissionType.AUTO, 6, [CarDriveType.FRONT])
		body = _make_body(CarBodyType.SEDAN)
		trim = _make_trim('Ambition', generation, engine, transmission, body)

		result = GuessCommonCarInfo._serialize_trim(trim)

		assert result.name == 'Ambition'
		assert result.parent.name == 'III'
		assert result.engine is not None
		assert result.engine.power == 110
		assert result.engine.type == 'Бензин, Атмосферный'
		assert result.transmission is not None
		assert result.transmission.type == 'АКПП'
		assert result.transmission.gears == 6
		assert result.drive_type == 'Передний'
		assert result.body_type == 'Седан'
		assert '1.6' in result.description
		assert '110 л.с.' in result.description
		assert 'АКПП' in result.description
		assert 'Передний' in result.description
		assert 'Седан' in result.description

	def test_trim_without_relations_falls_back_to_name(self) -> None:
		generation = _make_generation('III')
		trim = _make_trim('Base', generation, None, None, None)

		result = GuessCommonCarInfo._serialize_trim(trim)

		assert result.description == 'Base'
		assert result.engine is None
		assert result.transmission is None
		assert result.drive_type is None
		assert result.body_type is None

	def test_full_drive_type(self) -> None:
		generation = _make_generation('III')
		transmission = _make_transmission('AQ', VehicleTransmissionType.ROBOT, 7, [CarDriveType.FULL])
		trim = _make_trim('Sportline', generation, None, transmission, None)

		result = GuessCommonCarInfo._serialize_trim(trim)

		assert result.drive_type == 'Полный'
		assert result.transmission is not None
		assert result.transmission.type == 'Робот'

	def test_engine_without_volume_uses_name_in_description(self) -> None:
		"""Если volume=0 (или None-подобное) — description использует engine.name."""
		generation = _make_generation('I')
		engine = _make_engine('EM1', 0, 204, VehicleEngineType.ELECTRO, None)
		trim = _make_trim('E', generation, engine, None, None)

		result = GuessCommonCarInfo._serialize_trim(trim)

		assert 'EM1' in result.description
		assert '204 л.с.' in result.description

	def test_engine_without_power(self) -> None:
		"""Если мощность 0 — не добавляется '(0 л.с.)' в description."""
		generation = _make_generation('I')
		engine = _make_engine('X', 1400, 0, VehicleEngineType.PETROL, None)
		trim = _make_trim('Base', generation, engine, None, None)

		result = GuessCommonCarInfo._serialize_trim(trim)

		assert 'л.с.' not in result.description
		assert '1.4' in result.description

	def test_diesel_turbo_combined_flag(self) -> None:
		"""IntFlag DIESEL | TURBO → 'Дизель, Турбо'."""
		generation = _make_generation('II')
		engine = _make_engine('TDI', 2000, 150, VehicleEngineType.DIESEL | VehicleEngineType.TURBO, 320)
		trim = _make_trim('GT', generation, engine, None, None)

		result = GuessCommonCarInfo._serialize_trim(trim)

		assert result.engine is not None
		assert result.engine.type == 'Дизель, Турбо'
		assert 'Дизель, Турбо' in result.description

	def test_transmission_without_gears(self) -> None:
		"""Если gears=0 — не добавляется к типу КПП."""
		generation = _make_generation('I')
		transmission = _make_transmission('CVT-7', VehicleTransmissionType.VARIATOR, 0, [CarDriveType.FRONT])
		trim = _make_trim('Comfort', generation, None, transmission, None)

		result = GuessCommonCarInfo._serialize_trim(trim)

		assert result.transmission is not None
		assert result.transmission.type == 'Вариатор'
		assert 'Вариатор' in result.description
		# gears=0 → не дописывается число
		assert 'Вариатор 0' not in result.description

	def test_multiple_drive_types(self) -> None:
		"""Несколько типов привода через запятую."""
		generation = _make_generation('I')
		drives = [CarDriveType.FRONT, CarDriveType.FULL]
		transmission = _make_transmission('X', VehicleTransmissionType.MANUAL, 5, drives)
		trim = _make_trim('Adventure', generation, None, transmission, None)

		result = GuessCommonCarInfo._serialize_trim(trim)

		assert result.drive_type == 'Передний, Полный'


class TestEngineTypeLabel:
	"""Тесты хелпера ``_engine_type_label``."""

	def test_none_returns_none(self) -> None:
		assert _engine_type_label(None) is None

	def test_undefined_returns_none(self) -> None:
		assert _engine_type_label(VehicleEngineType.UNDEFINED) is None

	def test_single_flag(self) -> None:
		assert _engine_type_label(VehicleEngineType.DIESEL) == 'Дизель'

	def test_combined_flags(self) -> None:
		result = _engine_type_label(VehicleEngineType.PETROL | VehicleEngineType.TURBO)
		assert result is not None
		assert 'Бензин' in result
		assert 'Турбо' in result

	def test_all_fuel_types(self) -> None:
		result = _engine_type_label(VehicleEngineType.PETROL | VehicleEngineType.GAS)
		assert result is not None
		assert 'Бензин' in result
		assert 'Газ' in result


class TestDriveTypeLabel:
	"""Тесты хелпера ``_drive_type_label``."""

	def test_none_returns_none(self) -> None:
		assert _drive_type_label(None) is None

	def test_empty_list_returns_none(self) -> None:
		assert _drive_type_label([]) is None

	def test_single_value(self) -> None:
		assert _drive_type_label(CarDriveType.BACK) == 'Задний'

	def test_single_value_in_list(self) -> None:
		assert _drive_type_label([CarDriveType.FRONT]) == 'Передний'

	def test_multiple_values(self) -> None:
		result = _drive_type_label([CarDriveType.FRONT, CarDriveType.FULL])
		assert result == 'Передний, Полный'
