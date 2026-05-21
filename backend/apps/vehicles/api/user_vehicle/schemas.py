from typing import Any

from fastapi_utils.api_model import APIModel
from pydantic import Field, model_validator

from common.schemas.fields import ChoiceFieldSchema, ChoiceFieldWithParentSchema


class CreateUserVehicleByVinSchema(APIModel):
	"""Схема для создания ТС по VIN."""

	vin: str = Field(min_length=17, max_length=17, description='VIN-номер')


class CreateUserVehicleByChoiceSchema(APIModel):
	"""Схема для создания ТС с выбором комплектации."""

	brand_id: str = Field(description='ID бренда')
	series_id: str = Field(description='ID серии')
	generation_id: str = Field(description='ID поколения')
	trim_id: str | None = Field(default=None, description='ID комплектации')


class CreateUserVehicleManualSchema(APIModel):
	"""Схема для ручного создания ТС."""

	brand_id: str | None = Field(default=None, description='ID бренда')
	series_id: str | None = Field(default=None, description='ID серии')
	generation_id: str | None = Field(default=None, description='ID поколения')
	trim_id: str | None = Field(default=None, description='ID комплектации')
	production_year: int | None = Field(default=None, ge=1900, le=2100, description='Год выпуска')
	color: str | None = Field(default=None, description='Цвет')
	mileage: int | None = Field(default=None, ge=0, description='Пробег')
	is_mileage_in_miles: bool = Field(default=False, description='Пробег в милях')
	avg_fuel_consumption: float | None = Field(default=None, ge=0, description='Средний расход топлива')


class UserVehicleChoiceSchema(APIModel):
	"""Выбор пользователя при добавлении ТС по VIN."""

	brand: ChoiceFieldSchema = Field(description='Бренд')
	model: ChoiceFieldSchema = Field(description='Модель')
	generation: list[ChoiceFieldSchema] = Field(description='Поколения')
	configuration: list[ChoiceFieldWithParentSchema] = Field(
		default_factory=list,
		description='Комплектации',
	)


class UserVehicleDetailSchema(APIModel):
	"""Схема для отображения ТС пользователя."""

	id: str = Field(description='ID записи')
	vehicle_id: str | None = Field(default=None, description='ID транспортного средства')
	user_id: str = Field(description='ID пользователя')
	mileage: int | None = Field(default=None, description='Пробег')
	is_mileage_in_miles: bool = Field(default=False, description='Пробег в милях')
	avg_fuel_consumption: float | None = Field(default=None, description='Средний расход топлива')
	brand: str | None = Field(default=None, description='Бренд')
	series: str | None = Field(default=None, description='Модель/серия')
	generation: str | None = Field(default=None, description='Поколение')
	trim: str | None = Field(default=None, description='Комплектация')
	production_year: int | None = Field(default=None, description='Год выпуска')
	color: str | None = Field(default=None, description='Цвет')


class UserVehicleWithChoicesSchema(APIModel):
	"""ТС с вариантами выбора (когда несколько комплектаций)."""

	choices: list[UserVehicleChoiceSchema] = Field(description='Варианты выбора')
	vin: str = Field(description='VIN-номер')
	year: int = Field(description='Год выпуска')
	color: str | None = Field(default=None, description='Цвет')


class UserVehicleListSchema(APIModel):
	"""Минимальная схема для списка ТС пользователя."""

	id: str = Field(description='ID записи')
	vehicle_id: str | None = Field(default=None, description='ID транспортного средства')
	mileage: int | None = Field(default=None, description='Пробег')
	is_mileage_in_miles: bool = Field(default=False, description='Пробег в милях')
	brand: str | None = Field(default=None, description='Бренд')
	series: str | None = Field(default=None, description='Модель/серия')
	generation: str | None = Field(default=None, description='Поколение')

	@model_validator(mode='before')
	@classmethod
	def convert_user_vehicle_list(cls, data: Any) -> Any:
		"""Convert UserVehicle ORM model to list schema."""
		if hasattr(data, 'id'):
			brand_name = None
			series_name = None
			generation_name = None

			if hasattr(data, 'generation') and data.generation:
				generation_name = data.generation.name
				if hasattr(data.generation, 'series') and data.generation.series:
					series_name = data.generation.series.name
					if hasattr(data.generation.series, 'brand') and data.generation.series.brand:
						brand_name = data.generation.series.brand.name

			return {
				'id': str(data.id),
				'vehicle_id': str(data.vehicle_id) if data.vehicle_id else None,
				'mileage': getattr(data, 'mileage', None),
				'is_mileage_in_miles': getattr(data, 'is_mileage_in_miles', False),
				'brand': brand_name,
				'series': series_name,
				'generation': generation_name,
			}
		return data
