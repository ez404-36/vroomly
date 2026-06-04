"""Tests for car_info mappers — представление подобранных по VIN данных ТС.

Покрывает человекочитаемые метки (двигатель/привод) и сборку ``TrimChoiceSchema``
с готовой строкой ``description``.
"""

from typing import Any
from unittest.mock import MagicMock
from uuid import uuid4

from apps.vehicles.api.car_info.mappers import (
	drive_type_label,
	engine_type_label,
	to_guess_by_vin_response,
	trim_to_choice,
)
from apps.vehicles.models.car.car_trim import CarTrim
from apps.vehicles.models.car.enums import CarBodyType, CarDriveType
from apps.vehicles.models.node.body_node import CarBodyNode
from apps.vehicles.models.node.engine_node import EngineNode
from apps.vehicles.models.node.transmission_node import CarTransmissionNode
from apps.vehicles.models.vehicle.enums import VehicleEngineType, VehicleTransmissionType
from apps.vehicles.models.vehicle.vehicle_generation import VehicleGeneration


def _make_generation(name: str) -> Any:
	stub = MagicMock(spec=VehicleGeneration)
	stub.id = uuid4()
	stub.name = name
	return stub


def _make_engine(name: str, volume: int, power: int, engine_type: VehicleEngineType, torque: int | None) -> Any:
	stub = MagicMock(spec=EngineNode)
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
	stub = MagicMock(spec=CarTransmissionNode)
	stub.id = uuid4()
	stub.name = name
	stub.type = transmission_type
	stub.gears = gears
	stub.drive_types = drive_types
	return stub


def _make_body(body_type: CarBodyType) -> Any:
	stub = MagicMock(spec=CarBodyNode)
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


class TestTrimToChoice:
	"""``trim_to_choice`` собирает расширенные данные о комплектации."""

	def test_full_trim(self) -> None:
		generation = _make_generation('III')
		engine = _make_engine('CWVA', 1600, 110, VehicleEngineType.PETROL | VehicleEngineType.ATMOSPHERIC, 155)
		transmission = _make_transmission('0AM', VehicleTransmissionType.AUTO, 6, [CarDriveType.FRONT])
		body = _make_body(CarBodyType.SEDAN)
		trim = _make_trim('Ambition', generation, engine, transmission, body)

		result = trim_to_choice(trim)

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

		result = trim_to_choice(trim)

		assert result.description == 'Base'
		assert result.engine is None
		assert result.transmission is None
		assert result.drive_type is None
		assert result.body_type is None

	def test_full_drive_type(self) -> None:
		generation = _make_generation('III')
		transmission = _make_transmission('AQ', VehicleTransmissionType.ROBOT, 7, [CarDriveType.FULL])
		trim = _make_trim('Sportline', generation, None, transmission, None)

		result = trim_to_choice(trim)

		assert result.drive_type == 'Полный'
		assert result.transmission is not None
		assert result.transmission.type == 'Робот'

	def test_engine_without_volume_uses_name_in_description(self) -> None:
		"""Если volume=0 (или None-подобное) — description использует engine.name."""
		generation = _make_generation('I')
		engine = _make_engine('EM1', 0, 204, VehicleEngineType.ELECTRO, None)
		trim = _make_trim('E', generation, engine, None, None)

		result = trim_to_choice(trim)

		assert 'EM1' in result.description
		assert '204 л.с.' in result.description

	def test_engine_without_power(self) -> None:
		"""Если мощность 0 — не добавляется '(0 л.с.)' в description."""
		generation = _make_generation('I')
		engine = _make_engine('X', 1400, 0, VehicleEngineType.PETROL, None)
		trim = _make_trim('Base', generation, engine, None, None)

		result = trim_to_choice(trim)

		assert 'л.с.' not in result.description
		assert '1.4' in result.description

	def test_diesel_turbo_combined_flag(self) -> None:
		"""IntFlag DIESEL | TURBO → 'Дизель, Турбо'."""
		generation = _make_generation('II')
		engine = _make_engine('TDI', 2000, 150, VehicleEngineType.DIESEL | VehicleEngineType.TURBO, 320)
		trim = _make_trim('GT', generation, engine, None, None)

		result = trim_to_choice(trim)

		assert result.engine is not None
		assert result.engine.type == 'Дизель, Турбо'
		assert 'Дизель, Турбо' in result.description

	def test_transmission_without_gears(self) -> None:
		"""Если gears=0 — не добавляется к типу КПП."""
		generation = _make_generation('I')
		transmission = _make_transmission('CVT-7', VehicleTransmissionType.VARIATOR, 0, [CarDriveType.FRONT])
		trim = _make_trim('Comfort', generation, None, transmission, None)

		result = trim_to_choice(trim)

		assert result.transmission is not None
		assert result.transmission.type == 'Вариатор'
		assert 'Вариатор' in result.description
		assert 'Вариатор 0' not in result.description

	def test_multiple_drive_types(self) -> None:
		"""Несколько типов привода через запятую."""
		generation = _make_generation('I')
		drives = [CarDriveType.FRONT, CarDriveType.FULL]
		transmission = _make_transmission('X', VehicleTransmissionType.MANUAL, 5, drives)
		trim = _make_trim('Adventure', generation, None, transmission, None)

		result = trim_to_choice(trim)

		assert result.drive_type == 'Передний, Полный'


class TestEngineTypeLabel:
	"""Тесты хелпера ``engine_type_label``."""

	def test_none_returns_none(self) -> None:
		assert engine_type_label(None) is None

	def test_undefined_returns_none(self) -> None:
		assert engine_type_label(VehicleEngineType.UNDEFINED) is None

	def test_single_flag(self) -> None:
		assert engine_type_label(VehicleEngineType.DIESEL) == 'Дизель'

	def test_combined_flags(self) -> None:
		result = engine_type_label(VehicleEngineType.PETROL | VehicleEngineType.TURBO)
		assert result is not None
		assert 'Бензин' in result
		assert 'Турбо' in result

	def test_all_fuel_types(self) -> None:
		result = engine_type_label(VehicleEngineType.PETROL | VehicleEngineType.GAS)
		assert result is not None
		assert 'Бензин' in result
		assert 'Газ' in result


class TestDriveTypeLabel:
	"""Тесты хелпера ``drive_type_label``."""

	def test_none_returns_none(self) -> None:
		assert drive_type_label(None) is None

	def test_empty_list_returns_none(self) -> None:
		assert drive_type_label([]) is None

	def test_single_value(self) -> None:
		assert drive_type_label(CarDriveType.BACK) == 'Задний'

	def test_single_value_in_list(self) -> None:
		assert drive_type_label([CarDriveType.FRONT]) == 'Передний'

	def test_multiple_values(self) -> None:
		result = drive_type_label([CarDriveType.FRONT, CarDriveType.FULL])
		assert result == 'Передний, Полный'


class TestToGuessByVinResponse:
	"""Тесты сборки ``GuessByVinResponseSchema`` из подбора и сырых данных VIN."""

	@staticmethod
	def _car_info(vin: str, year: int, color: str) -> Any:
		from apps.vehicles.integrations.car_info_by_vin.schema import CarInfoByVinDataSchema

		return CarInfoByVinDataSchema(
			model='Лада Веста',
			year=year,
			frame=None,
			vin=vin,
			carplate='',
			color=color,
			type='',
			volume=1600,
			power=106,
			frame_id=0,
			vehicle_type='',
		)

	@staticmethod
	def _guess() -> Any:
		from apps.vehicles.services.guess_common_car_info import GuessCommonCarInfoSchema
		from common.schemas.fields import ChoiceFieldSchema

		return GuessCommonCarInfoSchema(
			brand=ChoiceFieldSchema(id=str(uuid4()), name='Lada'),
			model=ChoiceFieldSchema(id=str(uuid4()), name='Vesta'),
			generations=[ChoiceFieldSchema(id=str(uuid4()), name='I')],
			trims=[],
		)

	def test_combines_guess_and_raw_vin_fields(self) -> None:
		"""Подбор даёт бренд/модель/поколения, VIN-данные — vin/год/цвет."""
		guess = self._guess()
		car_info = self._car_info(vin='X' * 17, year=2021, color='Белый')

		result = to_guess_by_vin_response(guess, car_info)

		assert result.brand == guess.brand
		assert result.model == guess.model
		assert result.generations == guess.generations
		assert result.trims == guess.trims
		assert result.vin == 'X' * 17
		assert result.year == 2021
		assert result.color == 'Белый'
