"""Tests for UserVehicle API endpoints."""


from unittest.mock import MagicMock
from uuid import UUID

import pytest

from apps.vehicles.api.user_vehicle.endpoints import (
    _build_brand_schema,
    _build_engine_schema,
    _build_generation_schema,
    _build_series_schema,
    _build_transmission_schema,
    _build_trim_schema,
    _build_user_vehicle_full_schema,
    _build_user_vehicle_list_schema,
    _get_avg_fuel,
)
from apps.vehicles.models.car.car_trim import CarTrim
from apps.vehicles.models.car.car_transmission import CarTransmission
from apps.vehicles.models.vehicle.engine import VehicleEngine
from apps.vehicles.models.vehicle.user_vehicle import UserVehicle
from common.schemas.fields import ChoiceFieldSchema

from apps.vehicles.api.user_vehicle.schemas import (
    BrandSchema,
    CreateUserVehicleByChoiceSchema,
    CreateUserVehicleByVinSchema,
    CreateUserVehicleManualSchema,
    EngineSchema,
    GenerationSchema,
    SeriesSchema,
    TrimSchema,
    TransmissionSchema,
    UserVehicleChoiceSchema,
    UserVehicleDetailFullSchema,
    UserVehicleDetailSchema,
    UserVehicleListSchema,
    UserVehicleWithChoicesSchema,
)


class TestCreateUserVehicleByVinSchema:
    """Tests for CreateUserVehicleByVinSchema validation."""

    def test_valid_vin(self):
        """Should accept valid 17-character VIN."""
        schema = CreateUserVehicleByVinSchema(vin='1HGBH41JXMN109186')
        assert schema.vin == '1HGBH41JXMN109186'

    def test_vin_too_short(self):
        """Should reject VIN shorter than 17 characters."""
        with pytest.raises(Exception):
            CreateUserVehicleByVinSchema(vin='ABC123')

    def test_vin_too_long(self):
        """Should reject VIN longer than 17 characters."""
        with pytest.raises(Exception):
            CreateUserVehicleByVinSchema(vin='1HGBH41JXMN10918612345')


class TestCreateUserVehicleByChoiceSchema:
    """Tests for CreateUserVehicleByChoiceSchema validation."""

    def test_valid_choice(self):
        """Should accept valid choice data."""
        schema = CreateUserVehicleByChoiceSchema(
            brand_id='123e4567-e89b-12d3-a456-426614174000',
            series_id='123e4567-e89b-12d3-a456-426614174001',
            generation_id='123e4567-e89b-12d3-a456-426614174002',
        )
        assert schema.brand_id == '123e4567-e89b-12d3-a456-426614174000'
        assert schema.trim_id is None

    def test_choice_with_trim(self):
        """Should accept choice data with trim_id."""
        schema = CreateUserVehicleByChoiceSchema(
            brand_id='123e4567-e89b-12d3-a456-426614174000',
            series_id='123e4567-e89b-12d3-a456-426614174001',
            generation_id='123e4567-e89b-12d3-a456-426614174002',
            trim_id='123e4567-e89b-12d3-a456-426614174003',
        )
        assert schema.trim_id == '123e4567-e89b-12d3-a456-426614174003'


class TestCreateUserVehicleManualSchema:
    """Tests for CreateUserVehicleManualSchema validation."""

    def test_valid_manual_data(self):
        """Should accept valid manual data."""
        schema = CreateUserVehicleManualSchema(
            brand_id='123e4567-e89b-12d3-a456-426614174000',
            series_id='123e4567-e89b-12d3-a456-426614174001',
            generation_id='123e4567-e89b-12d3-a456-426614174002',
            production_year=2020,
            color='Серебристый',
        )
        assert schema.production_year == 2020
        assert schema.color == 'Серебристый'

    def test_minimal_manual_data(self):
        """Should accept minimal manual data (empty)."""
        schema = CreateUserVehicleManualSchema()
        assert schema.brand_id is None
        assert schema.series_id is None
        assert schema.generation_id is None
        assert schema.production_year is None
        assert schema.color is None

    def test_production_year_valid_range(self):
        """Should accept year within valid range."""
        schema = CreateUserVehicleManualSchema(production_year=2023)
        assert schema.production_year == 2023

    def test_production_year_too_early(self):
        """Should reject year before 1900."""
        with pytest.raises(Exception):
            CreateUserVehicleManualSchema(production_year=1800)

    def test_production_year_too_late(self):
        """Should reject year after 2100."""
        with pytest.raises(Exception):
            CreateUserVehicleManualSchema(production_year=2200)


class TestUserVehicleListSchema:
    """Tests for UserVehicleListSchema."""

    def test_create_list_schema(self):
        """Should create list schema with minimal fields."""
        schema = UserVehicleListSchema(
            id='123e4567-e89b-12d3-a456-426614174000',
            mileage=50000,
            is_mileage_in_miles=False,
            brand='Toyota',
            series='Camry',
            generation='X50',
        )
        assert schema.brand == 'Toyota'
        assert schema.series == 'Camry'
        assert schema.mileage == 50000

    def test_create_list_schema_minimal(self):
        """Should create list schema with minimal fields only."""
        schema = UserVehicleListSchema(
            id='123e4567-e89b-12d3-a456-426614174000',
        )
        assert schema.mileage is None
        assert schema.brand is None
        assert schema.series is None
        assert schema.generation is None


class TestUserVehicleWithChoicesSchema:
    """Tests for UserVehicleWithChoicesSchema."""

    def test_create_with_choices(self):
        """Should create schema with choices."""
        schema = UserVehicleWithChoicesSchema(
            choices=[
                UserVehicleChoiceSchema(
                    brand=ChoiceFieldSchema(id='1', name='Skoda'),
                    model=ChoiceFieldSchema(id='2', name='Octavia'),
                    generation=[
                        ChoiceFieldSchema(id='3', name='III'),
                    ],
                    configuration=[],
                ),
            ],
            vin='1HGBH41JXMN109186',
            year=2020,
            color='Серебристый',
        )
        assert len(schema.choices) == 1
        assert schema.choices[0].brand.name == 'Skoda'
        assert schema.vin == '1HGBH41JXMN109186'
        assert schema.year == 2020

    def test_create_with_choices_multiple_generations(self):
        """Should create schema with multiple generations."""
        schema = UserVehicleWithChoicesSchema(
            choices=[
                UserVehicleChoiceSchema(
                    brand=ChoiceFieldSchema(id='1', name='Skoda'),
                    model=ChoiceFieldSchema(id='2', name='Octavia'),
                    generation=[
                        ChoiceFieldSchema(id='3', name='II'),
                        ChoiceFieldSchema(id='4', name='III'),
                    ],
                    configuration=[],
                ),
            ],
            vin='1HGBH41JXMN109186',
            year=2015,
            color=None,
        )
        assert len(schema.choices[0].generation) == 2
        assert schema.color is None


class TestGetAvgFuel:
    """Tests for _get_avg_fuel helper function."""

    def test_get_avg_fuel_with_value(self):
        """Should return float when avg_fuel_consumption has value."""
        from decimal import Decimal
        mock_vehicle = MagicMock(spec=UserVehicle)
        mock_vehicle.avg_fuel_consumption = Decimal('7.50')
        result = _get_avg_fuel(mock_vehicle)
        assert result == 7.5
        assert isinstance(result, float)

    def test_get_avg_fuel_none(self):
        """Should return None when avg_fuel_consumption is None."""
        mock_vehicle = MagicMock(spec=UserVehicle)
        mock_vehicle.avg_fuel_consumption = None
        result = _get_avg_fuel(mock_vehicle)
        assert result is None


class TestBuildUserVehicleListSchema:
    """Tests for _build_user_vehicle_list_schema helper function."""

    def test_build_list_schema_with_relations(self):
        """Should build list schema with relations."""
        mock_brand = MagicMock()
        mock_brand.name = 'Toyota'
        mock_series = MagicMock()
        mock_series.name = 'Camry'
        mock_series.brand = mock_brand
        mock_generation = MagicMock()
        mock_generation.name = 'X50'
        mock_generation.series = mock_series

        mock_user_vehicle = MagicMock(spec=UserVehicle)
        mock_user_vehicle.id = UUID('123e4567-e89b-12d3-a456-426614174000')
        mock_user_vehicle.mileage = 50000
        mock_user_vehicle.is_mileage_in_miles = False
        mock_user_vehicle.generation = mock_generation

        result = _build_user_vehicle_list_schema(mock_user_vehicle)

        assert result.brand == 'Toyota'
        assert result.series == 'Camry'
        assert result.generation == 'X50'
        assert result.mileage == 50000

    def test_build_list_schema_without_relations(self):
        """Should build list schema with None values when relations are missing."""
        mock_user_vehicle = MagicMock(spec=UserVehicle)
        mock_user_vehicle.id = UUID('123e4567-e89b-12d3-a456-426614174000')
        mock_user_vehicle.mileage = None
        mock_user_vehicle.is_mileage_in_miles = False
        mock_user_vehicle.generation = None

        result = _build_user_vehicle_list_schema(mock_user_vehicle)

        assert result.brand is None
        assert result.series is None
        assert result.generation is None


class TestBuildEngineSchema:
    """Tests for _build_engine_schema helper function."""

    def test_build_engine_schema(self):
        """Should build engine schema from model."""
        from apps.vehicles.models.vehicle.enums import VehicleEngineType, VehicleEngineGRMType

        mock_engine = MagicMock(spec=VehicleEngine)
        mock_engine.id = UUID('123e4567-e89b-12d3-a456-426614174000')
        mock_engine.name = '1.8 TFSI'
        mock_engine.volume = 1798
        mock_engine.power = 180
        mock_engine.type = VehicleEngineType.PETROL | VehicleEngineType.TURBO
        mock_engine.eco_class = 'Euro 6'
        mock_engine.cylinders = 4
        mock_engine.valves = 16
        mock_engine.torque = 320
        mock_engine.grm_drive_type = VehicleEngineGRMType.BELT
        mock_engine.phase_regulator_type = None

        result = _build_engine_schema(mock_engine)

        assert result.name == '1.8 TFSI'
        assert result.volume == 1798
        assert result.power == 180
        assert 'Бензиновый' in result.type
        assert 'Турбированный' in result.type
        assert result.eco_class == 'Euro 6'
        assert result.grm_drive_type == 'Ремень'


class TestBuildTransmissionSchema:
    """Tests for _build_transmission_schema helper function."""

    def test_build_transmission_schema(self):
        """Should build transmission schema from model."""
        from apps.vehicles.models.car.enums import CarDriveType
        from apps.vehicles.models.vehicle.enums import VehicleTransmissionType

        mock_transmission = MagicMock(spec=CarTransmission)
        mock_transmission.id = UUID('123e4567-e89b-12d3-a456-426614174000')
        mock_transmission.name = '7-ступ. S-tronic'
        mock_transmission.index = '0D9'
        mock_transmission.type = VehicleTransmissionType.ROBOT
        mock_transmission.gears = 7
        mock_transmission.drive_types = [CarDriveType.FRONT, CarDriveType.FULL]
        mock_transmission.torque = 400

        result = _build_transmission_schema(mock_transmission)

        assert result.name == '7-ступ. S-tronic'
        assert result.type == 'Робот'
        assert result.gears == 7
        assert 'Передний' in result.drive_types
        assert 'Полный' in result.drive_types


class TestBuildTrimSchema:
    """Tests for _build_trim_schema helper function."""

    def test_build_trim_schema(self):
        """Should build trim schema from model."""
        from apps.vehicles.models.car.enums import CarDriveType
        from decimal import Decimal

        mock_trim = MagicMock(spec=CarTrim)
        mock_trim.id = UUID('123e4567-e89b-12d3-a456-426614174000')
        mock_trim.name = 'Sport'
        mock_trim.avg_fuel_consumption = Decimal('7.5')
        mock_trim.acceleration = Decimal('7.2')
        mock_trim.drive_type = CarDriveType.FRONT
        mock_trim.body_str = 'Седан'
        mock_trim.clearance = 150

        result = _build_trim_schema(mock_trim)

        assert result.name == 'Sport'
        assert result.avg_fuel_consumption == 7.5
        assert result.acceleration == 7.2
        assert result.drive_type == 'Передний'
        assert result.body_str == 'Седан'
        assert result.clearance == 150


class TestBuildGenerationSchema:
    """Tests for _build_generation_schema helper function."""

    def test_build_generation_schema(self):
        """Should build generation schema."""
        mock_generation = MagicMock()
        mock_generation.id = UUID('123e4567-e89b-12d3-a456-426614174000')
        mock_generation.name = 'X50'
        mock_generation.is_restyling = False
        mock_generation.start_year = 2018
        mock_generation.end_year = 2023

        result = _build_generation_schema(mock_generation)

        assert result.name == 'X50'
        assert result.is_restyling is False
        assert result.start_year == 2018
        assert result.end_year == 2023


class TestBuildSeriesSchema:
    """Tests for _build_series_schema helper function."""

    def test_build_series_schema(self):
        """Should build series schema."""
        mock_series = MagicMock()
        mock_series.id = UUID('123e4567-e89b-12d3-a456-426614174000')
        mock_series.name = 'Camry'

        result = _build_series_schema(mock_series)

        assert result.name == 'Camry'


class TestBuildBrandSchema:
    """Tests for _build_brand_schema helper function."""

    def test_build_brand_schema(self):
        """Should build brand schema."""
        mock_brand = MagicMock()
        mock_brand.id = UUID('123e4567-e89b-12d3-a456-426614174000')
        mock_brand.name = 'Toyota'
        mock_brand.abbreviation = 'TYT'

        result = _build_brand_schema(mock_brand)

        assert result.name == 'Toyota'
        assert result.abbreviation == 'TYT'


class TestBuildUserVehicleFullSchema:
    """Tests for _build_user_vehicle_full_schema helper function."""

    def test_build_full_schema(self):
        """Should build full detail schema with all related data."""
        mock_brand = MagicMock()
        mock_brand.id = UUID('123e4567-e89b-12d3-a456-426614174001')
        mock_brand.name = 'Toyota'
        mock_brand.abbreviation = 'TYT'
        mock_series = MagicMock()
        mock_series.id = UUID('123e4567-e89b-12d3-a456-426614174002')
        mock_series.name = 'Camry'
        mock_series.brand = mock_brand
        mock_generation = MagicMock()
        mock_generation.id = UUID('123e4567-e89b-12d3-a456-426614174003')
        mock_generation.name = 'X50'
        mock_generation.is_restyling = False
        mock_generation.start_year = 2018
        mock_generation.end_year = 2023
        mock_generation.series = mock_series

        mock_vehicle = MagicMock()
        mock_vehicle.production_year = 2020
        mock_vehicle.color = 'Белый'

        mock_user_vehicle = MagicMock(spec=UserVehicle)
        mock_user_vehicle.id = UUID('123e4567-e89b-12d3-a456-426614174000')
        mock_user_vehicle.vehicle_id = None
        mock_user_vehicle.user_id = UUID('123e4567-e89b-12d3-a456-426614174005')
        mock_user_vehicle.mileage = 50000
        mock_user_vehicle.is_mileage_in_miles = False
        mock_user_vehicle.avg_fuel_consumption = None
        mock_user_vehicle.generation = mock_generation
        mock_user_vehicle.vehicle = mock_vehicle

        result = _build_user_vehicle_full_schema(mock_user_vehicle)

        assert result.id == str(mock_user_vehicle.id)
        assert result.mileage == 50000
        assert result.production_year == 2020
        assert result.color == 'Белый'
        assert result.brand is not None
        assert result.brand.name == 'Toyota'
        assert result.series is not None
        assert result.series.name == 'Camry'
        assert result.generation is not None
        assert result.generation.name == 'X50'
