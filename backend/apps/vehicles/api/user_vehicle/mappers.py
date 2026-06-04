"""Преобразование ORM ``UserVehicle`` → Pydantic-схемы.

Слой представления: маппинг загруженных ORM-объектов в Detail-схему.
Не содержит ни доступа к данным, ни бизнес-логики.
"""

from decimal import Decimal

from apps.vehicles.api.user_vehicle.schemas import UserVehicleDetailSchema, UserVehicleListSchema
from apps.vehicles.models.car.car_spec import CarSpec
from apps.vehicles.models.vehicle.user_vehicle import UserVehicle

TrimChain = tuple[str | None, str | None, str | None, str | None]


def to_float(value: Decimal | float | int | None) -> float | None:
	"""Привести ``Decimal``/``None`` к ``float`` (или вернуть ``None``)."""
	if value is None:
		return None
	return float(value)


def resolve_trim_chain(user_vehicle: UserVehicle) -> TrimChain:
	"""
	Резолвит цепочку Brand → Series → Generation → Trim для загруженного ``UserVehicle``.

	Возвращает кортеж ``(brand_name, series_name, generation_name, trim_name)``.
	Каждое поле — ``None``, если соответствующая связь не загружена / отсутствует.
	"""
	brand_name: str | None = None
	series_name: str | None = None
	generation_name: str | None = None
	trim_name: str | None = None

	vehicle = user_vehicle.vehicle
	if vehicle is None:
		return brand_name, series_name, generation_name, trim_name

	spec: CarSpec | None = getattr(vehicle, 'car_spec', None)
	if spec is None:
		return brand_name, series_name, generation_name, trim_name

	trim = spec.trim
	if trim is None:
		return brand_name, series_name, generation_name, trim_name
	trim_name = trim.name

	generation = trim.generation
	if generation is not None:
		generation_name = generation.name
		series = generation.series
		if series is not None:
			series_name = series.name
			brand = series.brand
			if brand is not None:
				brand_name = brand.name

	return brand_name, series_name, generation_name, trim_name


def user_vehicle_to_detail(user_vehicle: UserVehicle) -> UserVehicleDetailSchema:
	"""Конвертирует ORM ``UserVehicle`` (с подгруженными связями) в Detail-схему."""
	vehicle = user_vehicle.vehicle
	mileage = vehicle.mileage if vehicle is not None else None
	is_mileage_in_miles = vehicle.is_mileage_in_miles if vehicle is not None else False
	production_year = vehicle.production_year if vehicle is not None else None
	color = vehicle.color if vehicle is not None else None

	brand_name, series_name, generation_name, trim_name = resolve_trim_chain(user_vehicle)

	return UserVehicleDetailSchema(
		id=str(user_vehicle.id),
		vehicle_id=str(user_vehicle.vehicle_id) if user_vehicle.vehicle_id else None,
		user_id=str(user_vehicle.user_id),
		mileage=mileage,
		is_mileage_in_miles=is_mileage_in_miles,
		avg_fuel_consumption=to_float(user_vehicle.avg_fuel_consumption),
		brand=brand_name,
		series=series_name,
		generation=generation_name,
		trim=trim_name,
		production_year=production_year,
		color=color,
	)


def user_vehicle_to_list_item(user_vehicle: UserVehicle) -> UserVehicleListSchema:
	"""Конвертирует ORM ``UserVehicle`` в схему элемента списка.

	Сборку плоского представления выполняет ``model_validator`` схемы
	``UserVehicleListSchema`` (резолв цепочки brand→series→generation).
	"""
	return UserVehicleListSchema.model_validate(user_vehicle)


def user_vehicles_to_list(user_vehicles: list[UserVehicle]) -> list[UserVehicleListSchema]:
	"""Конвертирует список ORM ``UserVehicle`` в список схем элементов списка."""
	return [user_vehicle_to_list_item(user_vehicle) for user_vehicle in user_vehicles]
