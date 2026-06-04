"""Tests for catalog read repositories.

Ключевое поведение SRP/root-cause: репозитории строят запросы (фильтры,
сортировка, поиск, joinedload) и возвращают список/объект или ``None``, не
бросая ``HTTPException`` (HTTP-семантика остаётся в слое эндпоинтов).
"""

import asyncio
from typing import Any, Coroutine, TypeVar
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from apps.vehicles.repositories.car_trim import CarTrimRepository
from apps.vehicles.repositories.vehicle import VehicleRepository
from apps.vehicles.repositories.vehicle_brand import VehicleBrandRepository
from apps.vehicles.repositories.vehicle_generation import VehicleGenerationRepository
from apps.vehicles.repositories.vehicle_series import VehicleSeriesRepository

T = TypeVar('T')


def _run(coro: Coroutine[Any, Any, T]) -> T:
	return asyncio.run(coro)


async def _capture_all(captured: dict[str, Any], query: Any) -> list[Any]:
	captured['sql'] = str(query.compile(compile_kwargs={'literal_binds': True}))
	return []


class TestCarTrimRepository:
	def test_list_for_generation_filters_when_id_given(self):
		repo = CarTrimRepository()
		generation_id = uuid4()
		captured: dict[str, Any] = {}

		with patch.object(repo, '_fetch_all', new=lambda q: _capture_all(captured, q)):
			_run(repo.list_for_generation(generation_id))

		assert generation_id.hex in captured['sql']

	def test_list_for_generation_without_id_has_no_generation_filter(self):
		repo = CarTrimRepository()
		captured: dict[str, Any] = {}

		with patch.object(repo, '_fetch_all', new=lambda q: _capture_all(captured, q)):
			_run(repo.list_for_generation(None))

		assert 'WHERE' not in captured['sql']

	def test_get_by_id_returns_none_without_raising(self):
		repo = CarTrimRepository()
		with patch.object(repo, '_fetch_one', new=AsyncMock(return_value=None)):
			result = _run(repo.get_by_id(uuid4()))
		assert result is None


class TestVehicleSeriesRepository:
	def test_list_filtered_applies_brand_and_search(self):
		repo = VehicleSeriesRepository()
		brand_id = uuid4()
		captured: dict[str, Any] = {}

		with patch.object(repo, '_fetch_all', new=lambda q: _capture_all(captured, q)):
			_run(repo.list_filtered(brand_id=brand_id, search='golf'))

		sql = captured['sql']
		assert brand_id.hex in sql
		assert 'golf' in sql.lower()

	def test_list_filtered_without_brand_has_no_brand_filter(self):
		repo = VehicleSeriesRepository()
		captured: dict[str, Any] = {}

		with patch.object(repo, '_fetch_all', new=lambda q: _capture_all(captured, q)):
			_run(repo.list_filtered(brand_id=None, search=None))

		assert 'WHERE' not in captured['sql']

	def test_get_with_brand_returns_none_without_raising(self):
		repo = VehicleSeriesRepository()
		with patch.object(repo, '_fetch_one', new=AsyncMock(return_value=None)):
			result = _run(repo.get_with_brand(uuid4()))
		assert result is None


class TestVehicleGenerationRepository:
	def test_list_for_series_filters_when_id_given(self):
		repo = VehicleGenerationRepository()
		series_id = uuid4()
		captured: dict[str, Any] = {}

		with patch.object(repo, '_fetch_all', new=lambda q: _capture_all(captured, q)):
			_run(repo.list_for_series(series_id))

		assert series_id.hex in captured['sql']

	def test_list_for_series_without_id_has_no_series_filter(self):
		repo = VehicleGenerationRepository()
		captured: dict[str, Any] = {}

		with patch.object(repo, '_fetch_all', new=lambda q: _capture_all(captured, q)):
			_run(repo.list_for_series(None))

		assert 'WHERE' not in captured['sql']


class TestVehicleBrandRepository:
	def test_list_filtered_normalizes_country_to_upper(self):
		repo = VehicleBrandRepository()
		captured: dict[str, Any] = {}

		with patch.object(repo, '_fetch_all', new=lambda q: _capture_all(captured, q)):
			_run(repo.list_filtered(country='de'))

		sql = captured['sql']
		assert "'DE'" in sql
		assert "'de'" not in sql

	def test_list_filtered_applies_search(self):
		repo = VehicleBrandRepository()
		captured: dict[str, Any] = {}

		with patch.object(repo, '_fetch_all', new=lambda q: _capture_all(captured, q)):
			_run(repo.list_filtered(search='bmw'))

		assert 'bmw' in captured['sql'].lower()

	def test_list_filtered_without_country_has_no_country_filter(self):
		repo = VehicleBrandRepository()
		captured: dict[str, Any] = {}

		with patch.object(repo, '_fetch_all', new=lambda q: _capture_all(captured, q)):
			_run(repo.list_filtered(country=None))

		assert 'WHERE' not in captured['sql']


class TestVehicleRepository:
	def test_get_by_id_returns_none_without_raising(self):
		repo = VehicleRepository()
		with patch.object(repo, '_fetch_one', new=AsyncMock(return_value=None)):
			result = _run(repo.get_by_id(uuid4()))
		assert result is None

	def test_get_by_id_filters_by_id(self):
		repo = VehicleRepository()
		vehicle_id = uuid4()
		captured: dict[str, Any] = {}

		async def _capture_one(query: Any) -> None:
			captured['sql'] = str(query.compile(compile_kwargs={'literal_binds': True}))

		with patch.object(repo, '_fetch_one', new=_capture_one):
			_run(repo.get_by_id(vehicle_id))

		assert vehicle_id.hex in captured['sql']
