from pydantic import BaseModel, Field

from common.schemas.fields import ChoiceFieldSchema, ChoiceFieldWithParentSchema


class CreateUserVehicleByVinSchema(BaseModel):
	"""Схема для создания ТС по VIN."""

	vin: str = Field(min_length=17, max_length=17, description='VIN-номер')


class CreateUserVehicleByChoiceSchema(BaseModel):
	"""Схема для создания ТС с выбором комплектации."""

	brand_id: str = Field(description='ID бренда')
	series_id: str = Field(description='ID серии')
	generation_id: str = Field(description='ID поколения')
	trim_id: str | None = Field(default=None, description='ID комплектации')


class CreateUserVehicleManualSchema(BaseModel):
	"""Схема для ручного создания ТС."""

	brand_id: str | None = Field(default=None, description='ID бренда')
	series_id: str | None = Field(default=None, description='ID серии')
	generation_id: str | None = Field(default=None, description='ID поколения')
	trim_id: str | None = Field(default=None, description='ID комплектации')
	production_year: int | None = Field(default=None, ge=1900, le=2100, description='Год выпуска')
	color: str | None = Field(default=None, description='Цвет')


class UserVehicleChoiceSchema(BaseModel):
	"""Выбор пользователя при добавлении ТС по VIN."""

	brand: ChoiceFieldSchema = Field(description='Бренд')
	model: ChoiceFieldSchema = Field(description='Модель')
	generation: list[ChoiceFieldSchema] = Field(description='Поколения')
	configuration: list[ChoiceFieldWithParentSchema] = Field(
		default_factory=list,
		description='Комплектации',
	)


class UserVehicleDetailSchema(BaseModel):
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


class UserVehicleWithChoicesSchema(BaseModel):
	"""ТС с вариантами выбора (когда несколько комплектаций)."""

	choices: list[UserVehicleChoiceSchema] = Field(description='Варианты выбора')
	vin: str = Field(description='VIN-номер')
	year: int = Field(description='Год выпуска')
	color: str | None = Field(default=None, description='Цвет')
