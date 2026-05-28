from typing import Any

from fastapi_utils.api_model import APIModel
from pydantic import Field, model_validator

from common.schemas.fields import ChoiceFieldSchema, TrimChoiceSchema


class CreateUserVehicleSchema(APIModel):
	"""
	Схема входа для создания UserVehicle.

	Используется единственным POST ``/user-vehicles/``. Фронт собирает
	все поля сам — либо из ручного ввода, либо после предзаполнения
	из ``GET /vehicles/guess_by_vin``.
	"""

	generation_id: str | None = Field(default=None, description='ID поколения')
	trim_id: str | None = Field(default=None, description='ID комплектации')
	production_year: int = Field(ge=1885, le=2100, description='Год выпуска')
	color: str | None = Field(default=None, description='Цвет')
	mileage: int | None = Field(default=None, ge=0, description='Пробег')
	is_mileage_in_miles: bool = Field(default=False, description='Пробег в милях')
	avg_fuel_consumption: float | None = Field(default=None, ge=0, description='Средний расход топлива')
	vin: str | None = Field(default=None, min_length=17, max_length=17, description='VIN-номер')


class GuessByVinResponseSchema(APIModel):
	"""
	Ответ ``GET /vehicles/guess_by_vin``.

	Содержит предзаполнение для формы добавления ТС: подобранные
	из БД бренд/модель/поколения/комплектации + сырые данные с VIN-провайдера
	(сам VIN, год, цвет).
	"""

	brand: ChoiceFieldSchema = Field(description='Бренд')
	model: ChoiceFieldSchema = Field(description='Модель')
	generations: list[ChoiceFieldSchema] = Field(default_factory=list, description='Поколения')
	trims: list[TrimChoiceSchema] = Field(default_factory=list, description='Комплектации')
	vin: str = Field(description='VIN-номер')
	year: int = Field(description='Год выпуска (с VIN-провайдера)')
	color: str | None = Field(default=None, description='Цвет (с VIN-провайдера)')


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
		"""
		Конвертирует ORM ``UserVehicle`` в плоский dict для схемы списка.

		Резолвит цепочку:
		``UserVehicle.vehicle → Vehicle.car_spec → CarSpec.trim → CarTrim.generation
		→ VehicleGeneration.series → VehicleSeries.brand``.

		Если какая-то ссылка отсутствует — соответствующее поле остаётся ``None``.
		"""
		if not hasattr(data, 'id'):
			return data

		brand_name: str | None = None
		series_name: str | None = None
		generation_name: str | None = None
		mileage: int | None = None
		is_mileage_in_miles: bool = False

		vehicle = getattr(data, 'vehicle', None)
		if vehicle is not None:
			mileage = vehicle.mileage
			is_mileage_in_miles = vehicle.is_mileage_in_miles

			spec = getattr(vehicle, 'car_spec', None)
			if spec is not None:
				trim = getattr(spec, 'trim', None)
				if trim is not None:
					generation = getattr(trim, 'generation', None)
					if generation is not None:
						generation_name = generation.name
						series = getattr(generation, 'series', None)
						if series is not None:
							series_name = series.name
							brand = getattr(series, 'brand', None)
							if brand is not None:
								brand_name = brand.name

		return {
			'id': str(data.id),
			'vehicle_id': str(data.vehicle_id) if data.vehicle_id else None,
			'mileage': mileage,
			'is_mileage_in_miles': is_mileage_in_miles,
			'brand': brand_name,
			'series': series_name,
			'generation': generation_name,
		}
