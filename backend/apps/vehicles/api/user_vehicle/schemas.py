from fastapi_utils.api_model import APIModel
from pydantic import Field

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
	mileage: int | None = Field(default=None, description='Пробег')
	is_mileage_in_miles: bool = Field(default=False, description='Пробег в милях')
	brand: str | None = Field(default=None, description='Бренд')
	series: str | None = Field(default=None, description='Модель/серия')
	generation: str | None = Field(default=None, description='Поколение')


class EngineSchema(APIModel):
	"""Схема двигателя."""

	id: str = Field(description='ID двигателя')
	name: str = Field(description='Название двигателя')
	volume: int = Field(description='Рабочий объём (сс)')
	power: int = Field(description='Мощность (л.с)')
	type: list[str] = Field(default_factory=list, description='Тип двигателя')
	eco_class: str | None = Field(default=None, description='Экологический класс')
	cylinders: int | None = Field(default=None, description='Кол-во цилиндров')
	valves: int | None = Field(default=None, description='Кол-во клапанов')
	torque: int | None = Field(default=None, description='Крутящий момент (Нм)')
	grm_drive_type: str | None = Field(default=None, description='Тип привода ГРМ')
	phase_regulator_type: str | None = Field(default=None, description='Фазорегулятор')


class TransmissionSchema(APIModel):
	"""Схема трансмиссии."""

	id: str = Field(description='ID трансмиссии')
	name: str = Field(description='Название')
	index: str | None = Field(default=None, description='Заводской индекс')
	type: str = Field(description='Тип коробки передач')
	gears: int = Field(description='Количество передач')
	drive_types: list[str] = Field(default_factory=list, description='Типы привода')
	torque: int | None = Field(default=None, description='Крутящий момент (Нм)')


class TrimSchema(APIModel):
	"""Схема комплектации."""

	id: str = Field(description='ID комплектации')
	name: str = Field(description='Название комплектации')
	avg_fuel_consumption: float | None = Field(default=None, description='Средний расход топлива (по паспорту)')
	acceleration: float | None = Field(default=None, description='Разгон до 100 км/ч (по паспорту)')
	drive_type: str | None = Field(default=None, description='Тип привода')
	body_str: str | None = Field(default=None, description='Кузов автомобиля')
	clearance: int | None = Field(default=None, description='Клиренс')


class GenerationSchema(APIModel):
	"""Схема поколения."""

	id: str = Field(description='ID поколения')
	name: str = Field(description='Название поколения')
	is_restyling: bool = Field(default=False, description='Рестайлинг')
	start_year: int = Field(description='Начало продаж (год)')
	end_year: int | None = Field(default=None, description='Окончание продаж (год)')


class SeriesSchema(APIModel):
	"""Схема серии/модели."""

	id: str = Field(description='ID серии')
	name: str = Field(description='Название модели')


class BrandSchema(APIModel):
	"""Схема бренда."""

	id: str = Field(description='ID бренда')
	name: str = Field(description='Название бренда')
	abbreviation: str | None = Field(default=None, description='Аббревиатура')


class UserVehicleDetailFullSchema(APIModel):
	"""Полная схема ТС пользователя для детального просмотра."""

	id: str = Field(description='ID записи')
	vehicle_id: str | None = Field(default=None, description='ID транспортного средства')
	user_id: str = Field(description='ID пользователя')
	mileage: int | None = Field(default=None, description='Пробег')
	is_mileage_in_miles: bool = Field(default=False, description='Пробег в милях')
	avg_fuel_consumption: float | None = Field(default=None, description='Средний расход топлива')
	production_year: int | None = Field(default=None, description='Год выпуска')
	color: str | None = Field(default=None, description='Цвет')
	brand: BrandSchema | None = Field(default=None, description='Бренд')
	series: SeriesSchema | None = Field(default=None, description='Серия/модель')
	generation: GenerationSchema | None = Field(default=None, description='Поколение')
	trim: TrimSchema | None = Field(default=None, description='Комплектация')
	engine: EngineSchema | None = Field(default=None, description='Двигатель')
	transmission: TransmissionSchema | None = Field(default=None, description='Трансмиссия')
