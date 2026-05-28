"""Tests for UserVehicle API schemas and endpoint helpers."""

import asyncio
from decimal import Decimal
from typing import Any, Coroutine, TypeVar
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from apps.vehicles.api.car_info.endpoints import CarInfoByVinAPI
from apps.vehicles.api.user_vehicle.endpoints import (
	_resolve_trim_chain,
	_to_float,
	_user_vehicle_to_detail,
)
from apps.vehicles.api.user_vehicle.schemas import (
	CreateUserVehicleSchema,
	GuessByVinResponseSchema,
	UserVehicleDetailSchema,
	UserVehicleListSchema,
)
from apps.vehicles.integrations.car_info_by_vin.schema import CarInfoByVinDataSchema
from apps.vehicles.services.guess_common_car_info import GuessCommonCarInfoSchema
from common.schemas.fields import ChoiceFieldSchema, TrimChoiceSchema

T = TypeVar('T')


def _run(coro: Coroutine[Any, Any, T]) -> T:
	"""Запускает корутину в свежем event loop (без pytest-asyncio)."""
	return asyncio.run(coro)


class TestCreateUserVehicleSchema:
	"""Tests for CreateUserVehicleSchema validation."""

	def test_minimal_valid_data(self):
		"""Production_year обязателен; остальные поля опциональны."""
		schema = CreateUserVehicleSchema(production_year=2020)
		assert schema.production_year == 2020
		assert schema.generation_id is None
		assert schema.trim_id is None
		assert schema.vin is None
		assert schema.is_mileage_in_miles is False

	def test_full_valid_data(self):
		"""Все поля задаются успешно."""
		schema = CreateUserVehicleSchema(
			generation_id='123e4567-e89b-12d3-a456-426614174000',
			trim_id='123e4567-e89b-12d3-a456-426614174001',
			production_year=2020,
			color='Серебристый',
			mileage=50000,
			is_mileage_in_miles=False,
			avg_fuel_consumption=8.5,
			vin='1HGBH41JXMN109186',
		)
		assert schema.vin == '1HGBH41JXMN109186'
		assert schema.avg_fuel_consumption == 8.5

	def test_production_year_required(self):
		"""Без production_year — ошибка валидации (передаём пустой dict через model_validate)."""
		with pytest.raises(Exception):
			CreateUserVehicleSchema.model_validate({})

	def test_production_year_too_early(self):
		"""Год до 1885 — ошибка."""
		with pytest.raises(Exception):
			CreateUserVehicleSchema(production_year=1800)

	def test_production_year_too_late(self):
		"""Год после 2100 — ошибка."""
		with pytest.raises(Exception):
			CreateUserVehicleSchema(production_year=2200)

	def test_negative_mileage_rejected(self):
		"""Отрицательный пробег — ошибка."""
		with pytest.raises(Exception):
			CreateUserVehicleSchema(production_year=2020, mileage=-1)

	def test_negative_fuel_consumption_rejected(self):
		"""Отрицательный расход — ошибка."""
		with pytest.raises(Exception):
			CreateUserVehicleSchema(production_year=2020, avg_fuel_consumption=-1.0)

	def test_vin_wrong_length_rejected(self):
		"""VIN длиной не 17 — ошибка."""
		with pytest.raises(Exception):
			CreateUserVehicleSchema(production_year=2020, vin='ABC')


class TestGuessByVinResponseSchema:
	"""Tests for GuessByVinResponseSchema."""

	def test_minimal_response(self):
		"""Минимальный набор (пустые generations/trims)."""
		schema = GuessByVinResponseSchema(
			brand=ChoiceFieldSchema(id='1', name='Skoda'),
			model=ChoiceFieldSchema(id='2', name='Octavia'),
			vin='1HGBH41JXMN109186',
			year=2020,
		)
		assert schema.generations == []
		assert schema.trims == []
		assert schema.color is None

	def test_full_response(self):
		"""Полный набор с поколениями и комплектациями."""
		parent = ChoiceFieldSchema(id='gen1', name='III')
		schema = GuessByVinResponseSchema(
			brand=ChoiceFieldSchema(id='1', name='Skoda'),
			model=ChoiceFieldSchema(id='2', name='Octavia'),
			generations=[parent],
			trims=[TrimChoiceSchema(id='t1', name='Ambition', parent=parent, description='Ambition')],
			vin='1HGBH41JXMN109186',
			year=2020,
			color='Серебристый',
		)
		assert len(schema.generations) == 1
		assert len(schema.trims) == 1
		assert schema.trims[0].parent.name == 'III'


class TestToFloatHelper:
	"""Tests for _to_float."""

	def test_none(self):
		assert _to_float(None) is None

	def test_decimal(self):
		assert _to_float(Decimal('8.5')) == 8.5

	def test_int(self):
		assert _to_float(8) == 8.0


class TestResolveTrimChain:
	"""Tests for _resolve_trim_chain — резолв Brand→Series→Generation→Trim."""

	def test_no_vehicle(self):
		"""Без Vehicle — все None."""
		uv = MagicMock()
		uv.vehicle = None
		assert _resolve_trim_chain(uv) == (None, None, None, None)

	def test_vehicle_without_spec(self):
		"""Vehicle без CarSpec — все None."""
		uv = MagicMock()
		uv.vehicle = MagicMock(car_spec=None)
		assert _resolve_trim_chain(uv) == (None, None, None, None)

	def test_spec_without_trim(self):
		"""CarSpec без trim — все None."""
		uv = MagicMock()
		uv.vehicle = MagicMock(car_spec=MagicMock(trim=None))
		assert _resolve_trim_chain(uv) == (None, None, None, None)

	def test_full_chain(self):
		"""Полная цепочка резолвится."""
		brand = MagicMock()
		brand.name = 'Skoda'
		series = MagicMock()
		series.name = 'Octavia'
		series.brand = brand
		generation = MagicMock()
		generation.name = 'III'
		generation.series = series
		trim = MagicMock()
		trim.name = 'Ambition'
		trim.generation = generation
		spec = MagicMock(trim=trim)
		vehicle = MagicMock(car_spec=spec)
		uv = MagicMock(vehicle=vehicle)

		result = _resolve_trim_chain(uv)
		assert result == ('Skoda', 'Octavia', 'III', 'Ambition')


class TestUserVehicleToDetail:
	"""Tests for _user_vehicle_to_detail."""

	def test_minimal_vehicle(self):
		"""Минимальный Vehicle без spec — только базовые поля."""
		user_id = uuid4()
		uv_id = uuid4()
		vehicle_id = uuid4()
		vehicle = MagicMock(
			mileage=10000,
			is_mileage_in_miles=False,
			production_year=2020,
			color='Серебристый',
			car_spec=None,
		)
		uv = MagicMock(
			id=uv_id,
			vehicle_id=vehicle_id,
			user_id=user_id,
			avg_fuel_consumption=Decimal('8.5'),
			vehicle=vehicle,
		)

		result = _user_vehicle_to_detail(uv)
		assert isinstance(result, UserVehicleDetailSchema)
		assert result.mileage == 10000
		assert result.production_year == 2020
		assert result.color == 'Серебристый'
		assert result.avg_fuel_consumption == 8.5
		assert result.brand is None
		assert result.trim is None

	def test_no_vehicle(self):
		"""UserVehicle без Vehicle — все vehicle-поля None/default."""
		user_id = uuid4()
		uv = MagicMock(
			id=uuid4(),
			vehicle_id=None,
			user_id=user_id,
			avg_fuel_consumption=None,
			vehicle=None,
		)
		result = _user_vehicle_to_detail(uv)
		assert result.mileage is None
		assert result.is_mileage_in_miles is False
		assert result.production_year is None
		assert result.color is None
		assert result.avg_fuel_consumption is None
		assert result.vehicle_id is None


class TestUserVehicleListSchema:
	"""Tests for UserVehicleListSchema (with model_validator)."""

	def test_create_from_dict(self):
		"""Создание из готового dict."""
		schema = UserVehicleListSchema(
			id='123e4567-e89b-12d3-a456-426614174000',
			mileage=50000,
			is_mileage_in_miles=False,
			brand='Toyota',
			series='Camry',
			generation='X50',
		)
		assert schema.brand == 'Toyota'

	def test_create_minimal(self):
		"""Минимальный набор."""
		schema = UserVehicleListSchema(id='123e4567-e89b-12d3-a456-426614174000')
		assert schema.brand is None
		assert schema.mileage is None

	def test_convert_from_orm(self):
		"""Конвертирует ORM-объект через model_validator."""
		uv_id = uuid4()
		vehicle_id = uuid4()
		brand = MagicMock()
		brand.name = 'Skoda'
		series = MagicMock(brand=brand)
		series.name = 'Octavia'
		generation = MagicMock(series=series)
		generation.name = 'III'
		trim = MagicMock(generation=generation)
		spec = MagicMock(trim=trim)
		vehicle = MagicMock(car_spec=spec, mileage=42000, is_mileage_in_miles=True)
		orm = MagicMock(id=uv_id, vehicle_id=vehicle_id, vehicle=vehicle)

		schema = UserVehicleListSchema.model_validate(orm)
		assert schema.brand == 'Skoda'
		assert schema.series == 'Octavia'
		assert schema.generation == 'III'
		assert schema.mileage == 42000
		assert schema.is_mileage_in_miles is True


class TestGuessByVinEndpoint:
	"""Тесты на эндпоинт CarInfoByVinAPI.guess_by_vin (read-only)."""

	def test_returns_response_schema(self):
		"""Эндпоинт собирает GuessByVinResponseSchema из guess-сервиса и vin-провайдера."""
		car_info = CarInfoByVinDataSchema(
			model='Skoda Octavia',
			year=2020,
			frame='F1',
			vin='1HGBH41JXMN109186',
			carplate='A123BC',
			color='Серебристый',
			type='Sedan',
			volume=2,
			power=150,
			frame_id=1,
			vehicle_type='passenger',
		)
		guess_result = GuessCommonCarInfoSchema(
			brand=ChoiceFieldSchema(id='b1', name='Skoda'),
			model=ChoiceFieldSchema(id='m1', name='Octavia'),
			generations=[ChoiceFieldSchema(id='g1', name='III')],
			trims=[
				TrimChoiceSchema(
					id='t1',
					name='Ambition',
					parent=ChoiceFieldSchema(id='g1', name='III'),
					description='1.6 (110 л.с.) Бензин · АКПП 6 · Передний · Седан',
				),
			],
		)

		api = CarInfoByVinAPI.__new__(CarInfoByVinAPI)

		with (
			patch(
				'apps.vehicles.api.car_info.endpoints.CarInfoByVinProvider.get_info',
				return_value=car_info,
			),
			patch(
				'apps.vehicles.api.car_info.endpoints.GuessCommonCarInfo.get_from_vin01',
				new=AsyncMock(return_value=guess_result),
			),
		):
			result = _run(api.guess_by_vin(vin='1HGBH41JXMN109186'))

		assert isinstance(result, GuessByVinResponseSchema)
		assert result.vin == '1HGBH41JXMN109186'
		assert result.year == 2020
		assert result.color == 'Серебристый'
		assert result.brand.name == 'Skoda'
		assert result.model.name == 'Octavia'
		assert len(result.generations) == 1
		assert len(result.trims) == 1
