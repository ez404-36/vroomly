"""Tests for GuessCommonCarInfo — оркестрация подбора по данным VIN-провайдера.

После выделения слоёв (Фаза 4) доступ к данным живёт в ``CarCatalogRepository``/
``fuzzy_lookup``, представление — в ``api/car_info/mappers``. Здесь тестируется
только оркестрация: перевод → подбор бренда (с расширением префикса) → модель →
поколения → комплектации → сборка схемы.

Тесты на ``fuzzy_lookup`` — в ``repositories/test_fuzzy_lookup.py``;
на ``trim_to_choice``/метки — в ``api/test_car_info_mappers.py``.
"""

import asyncio
from typing import Any, Coroutine, TypeVar
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from apps.vehicles.integrations.car_info_by_vin.schema import CarInfoByVinDataSchema
from apps.vehicles.services.guess_common_car_info import (
	GuessCommonCarInfo,
	GuessCommonCarInfoError,
	GuessCommonCarInfoSchema,
)

T = TypeVar('T')

_CATALOG = 'apps.vehicles.services.guess_common_car_info.CarCatalogRepository'
_TRANSLATOR = 'apps.vehicles.services.guess_common_car_info.Translator'


def _run(coro: Coroutine[Any, Any, T]) -> T:
	return asyncio.run(coro)


def _make_choice(name: str) -> Any:
	stub = MagicMock()
	stub.id = uuid4()
	stub.name = name
	return stub


def _make_car_info(model: str, year: int = 2020) -> CarInfoByVinDataSchema:
	return CarInfoByVinDataSchema(
		model=model,
		year=year,
		frame='F1',
		vin='1HGBH41JXMN109186',
		carplate='A123BC',
		color='Серебристый',
		type='Sedan',
		volume=1600,
		power=110,
		frame_id=1,
		vehicle_type='passenger',
	)


def _identity_translator() -> Any:
	"""Translator-заглушка: translate(x) -> x (без обращения к сервису перевода)."""
	translator = MagicMock()
	translator.translate = MagicMock(side_effect=lambda text: text)
	return translator


def _make_catalog(**methods: Any) -> Any:
	catalog = MagicMock()
	for name, value in methods.items():
		setattr(catalog, name, value)
	return catalog


class TestGetFromVin01:
	def test_full_pipeline_assembles_schema(self) -> None:
		"""Полный happy-path: бренд+модель найдены, поколения/комплектации собраны в схему."""
		brand = _make_choice('Skoda')
		series = _make_choice('Octavia')
		generation = _make_choice('III')
		catalog = _make_catalog(
			find_brand=AsyncMock(return_value=brand),
			find_series=AsyncMock(return_value=series),
			list_generations=AsyncMock(return_value=[generation]),
			list_trims=AsyncMock(return_value=[]),
		)

		with (
			patch(_TRANSLATOR, return_value=_identity_translator()),
			patch(_CATALOG, return_value=catalog),
		):
			result = _run(GuessCommonCarInfo().get_from_vin01(_make_car_info('Skoda Octavia')))

		assert isinstance(result, GuessCommonCarInfoSchema)
		assert result.brand.name == 'Skoda'
		assert result.model.name == 'Octavia'
		assert len(result.generations) == 1
		catalog.find_series.assert_awaited_once()
		# find_series вызван с id найденного бренда.
		assert catalog.find_series.call_args.args[0] == brand.id

	def test_multiword_brand_resolution(self) -> None:
		"""Бренд из двух слов: первое слово не находится, префикс расширяется до двух."""
		brand = _make_choice('Land Rover')
		series = _make_choice('Discovery')
		catalog = _make_catalog(
			find_brand=AsyncMock(side_effect=[None, brand]),
			find_series=AsyncMock(return_value=series),
			list_generations=AsyncMock(return_value=[]),
			list_trims=AsyncMock(return_value=[]),
		)

		with (
			patch(_TRANSLATOR, return_value=_identity_translator()),
			patch(_CATALOG, return_value=catalog),
		):
			result = _run(GuessCommonCarInfo().get_from_vin01(_make_car_info('Land Rover Discovery')))

		assert result.brand.name == 'Land Rover'
		assert result.model.name == 'Discovery'
		assert catalog.find_brand.await_count == 2
		# Модель — это остаток после двух слов бренда.
		assert catalog.find_series.call_args.args[1] == 'Discovery'

	def test_brand_not_found_raises(self) -> None:
		catalog = _make_catalog(find_brand=AsyncMock(return_value=None))
		with (
			patch(_TRANSLATOR, return_value=_identity_translator()),
			patch(_CATALOG, return_value=catalog),
		):
			with pytest.raises(GuessCommonCarInfoError) as excinfo:
				_run(GuessCommonCarInfo().get_from_vin01(_make_car_info('НеизвестныйБренд')))

		assert 'марку' in str(excinfo.value)

	def test_series_not_found_raises(self) -> None:
		brand = _make_choice('Skoda')
		catalog = _make_catalog(
			find_brand=AsyncMock(return_value=brand),
			find_series=AsyncMock(return_value=None),
		)
		with (
			patch(_TRANSLATOR, return_value=_identity_translator()),
			patch(_CATALOG, return_value=catalog),
		):
			with pytest.raises(GuessCommonCarInfoError) as excinfo:
				_run(GuessCommonCarInfo().get_from_vin01(_make_car_info('Skoda НетТакой')))

		assert 'модель' in str(excinfo.value)
