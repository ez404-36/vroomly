"""Tests for UserVehicle API schemas."""

from uuid import UUID

import pytest

from apps.vehicles.api.user_vehicle.schemas import (
    CreateUserVehicleByChoiceSchema,
    CreateUserVehicleByVinSchema,
    CreateUserVehicleManualSchema,
    UserVehicleChoiceSchema,
    UserVehicleListSchema,
    UserVehicleWithChoicesSchema,
)
from common.schemas.fields import ChoiceFieldSchema


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