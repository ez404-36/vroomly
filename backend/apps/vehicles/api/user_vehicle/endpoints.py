from uuid import UUID

from fastapi_utils.cbv import cbv
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from apps.vehicles.api.routers import user_vehicle_router
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
from apps.vehicles.integrations.car_info_by_vin.provider import CarInfoByVinProvider
from apps.vehicles.models.car.car_trim import CarTrim
from apps.vehicles.models.car.car_transmission import CarTransmission
from apps.vehicles.models.vehicle.vehicle_engine import VehicleEngine
from apps.vehicles.models.vehicle.user_vehicle import UserVehicle
from apps.vehicles.services.guess_common_car_info import GuessCommonCarInfo
from common.orm.views.mixins import BaseAPI
from core.db import database


def _get_avg_fuel(user_vehicle: UserVehicle) -> float | None:
	"""Extract avg_fuel_consumption as float."""
	if user_vehicle.avg_fuel_consumption is None:
		return None
	return float(user_vehicle.avg_fuel_consumption)


def _build_user_vehicle_list_schema(user_vehicle: UserVehicle) -> UserVehicleListSchema:
	"""Build minimal schema for list endpoint."""
	brand_name = None
	series_name = None
	generation_name = None

	if user_vehicle.generation is not None:
		generation_name = user_vehicle.generation.name
		if user_vehicle.generation.series is not None:
			series_name = user_vehicle.generation.series.name
			if hasattr(user_vehicle.generation.series, 'brand') and user_vehicle.generation.series.brand is not None:
				brand_name = user_vehicle.generation.series.brand.name

	return UserVehicleListSchema(
		id=str(user_vehicle.id),
		mileage=user_vehicle.mileage,
		is_mileage_in_miles=user_vehicle.is_mileage_in_miles,
		brand=brand_name,
		series=series_name,
		generation=generation_name,
	)


def _build_engine_schema(engine: VehicleEngine) -> EngineSchema:
	"""Build engine schema from model."""
	engine_types = []
	if engine.type:
		if engine.type & 1:  # PETROL
			engine_types.append('Бензиновый')
		if engine.type & 2:  # DIESEL
			engine_types.append('Дизельный')
		if engine.type & 4:  # ELECTRO
			engine_types.append('Электрический')
		if engine.type & 8:  # GAS
			engine_types.append('Газовый')
		if engine.type & 16:  # ATMOSPHERIC
			engine_types.append('Атмосферный')
		if engine.type & 32:  # TURBO
			engine_types.append('Турбированный')

	grm_drive_type = None
	if engine.grm_drive_type:
		grm_types = []
		if engine.grm_drive_type & 1:  # BELT
			grm_types.append('Ремень')
		if engine.grm_drive_type & 2:  # CHAIN
			grm_types.append('Цепь')
		if engine.grm_drive_type & 4:  # GEARS
			grm_types.append('Шестерни')
		if engine.grm_drive_type & 64:  # WET_BELT
			grm_types.append('Мокрый ремень')
		if engine.grm_drive_type & 8:  # TWO_CHAINS
			grm_types.append('2 цепи')
		if engine.grm_drive_type & 128:  # TWO_BELTS
			grm_types.append('2 ремня')
		grm_drive_type = ', '.join(grm_types) if grm_types else None

	phase_regulator = None
	if engine.phase_regulator_type:
		phase_map = {1: 'На впуске', 2: 'На выпуске', 3: 'На обоих валах', 4: 'Сложная'}
		phase_regulator = phase_map.get(int(engine.phase_regulator_type))

	return EngineSchema(
		id=str(engine.id),
		name=engine.name,
		volume=engine.volume,
		power=engine.power,
		type=engine_types,
		eco_class=engine.eco_class,
		cylinders=engine.cylinders,
		valves=engine.valves,
		torque=engine.torque,
		grm_drive_type=grm_drive_type,
		phase_regulator_type=phase_regulator,
	)


def _build_transmission_schema(transmission: CarTransmission) -> TransmissionSchema:
	"""Build transmission schema from model."""
	trans_type = None
	if transmission.type:
		type_map = {1: 'Механика', 2: 'Автомат', 3: 'Робот', 4: 'Вариатор'}
		trans_type = type_map.get(int(transmission.type))

	drive_types = []
	if transmission.drive_types:
		for dt in transmission.drive_types:
			dt_map = {1: 'Передний', 2: 'Задний', 3: 'Полный'}
			drive_types.append(dt_map.get(int(dt), str(dt)))

	return TransmissionSchema(
		id=str(transmission.id),
		name=transmission.name,
		index=transmission.index,
		type=trans_type or 'Не определено',
		gears=transmission.gears,
		drive_types=drive_types,
		torque=transmission.torque,
	)


def _build_trim_schema(trim: CarTrim) -> TrimSchema:
	"""Build trim schema from model."""
	drive_type = None
	if trim.drive_type:
		dt_map = {1: 'Передний', 2: 'Задний', 3: 'Полный'}
		drive_type = dt_map.get(int(trim.drive_type))

	return TrimSchema(
		id=str(trim.id),
		name=trim.name,
		avg_fuel_consumption=float(trim.avg_fuel_consumption) if trim.avg_fuel_consumption else None,
		acceleration=float(trim.acceleration) if trim.acceleration else None,
		drive_type=drive_type,
		body_str=trim.body_str,
		clearance=trim.clearance,
	)


def _build_generation_schema(generation) -> GenerationSchema:
	"""Build generation schema from model."""
	return GenerationSchema(
		id=str(generation.id),
		name=generation.name,
		is_restyling=generation.is_restyling,
		start_year=generation.start_year,
		end_year=generation.end_year,
	)


def _build_series_schema(series) -> SeriesSchema:
	"""Build series schema from model."""
	return SeriesSchema(
		id=str(series.id),
		name=series.name,
	)


def _build_brand_schema(brand) -> BrandSchema:
	"""Build brand schema from model."""
	return BrandSchema(
		id=str(brand.id),
		name=brand.name,
		abbreviation=brand.abbreviation,
	)


def _build_user_vehicle_full_schema(user_vehicle: UserVehicle) -> UserVehicleDetailFullSchema:
	"""Build full detail schema with all related data."""
	brand = None
	series = None
	generation = None
	trim = None
	engine = None
	transmission = None
	production_year = None
	color = None

	if user_vehicle.generation is not None:
		generation = _build_generation_schema(user_vehicle.generation)
		if user_vehicle.generation.series is not None:
			series = _build_series_schema(user_vehicle.generation.series)
			if hasattr(user_vehicle.generation.series, 'brand') and user_vehicle.generation.series.brand is not None:
				brand = _build_brand_schema(user_vehicle.generation.series.brand)
		if hasattr(user_vehicle.generation, 'trims') and user_vehicle.generation.trims:
			first_trim = user_vehicle.generation.trims[0]
			trim = _build_trim_schema(first_trim)
			if hasattr(first_trim, 'transmission') and first_trim.transmission is not None:
				transmission = _build_transmission_schema(first_trim.transmission)
			if hasattr(first_trim, 'engine') and first_trim.engine is not None:
				engine = _build_engine_schema(first_trim.engine)

	if user_vehicle.vehicle is not None:
		production_year = user_vehicle.vehicle.production_year
		color = user_vehicle.vehicle.color

	return UserVehicleDetailFullSchema(
		id=str(user_vehicle.id),
		vehicle_id=str(user_vehicle.vehicle_id) if user_vehicle.vehicle_id else None,
		user_id=str(user_vehicle.user_id),
		mileage=user_vehicle.mileage,
		is_mileage_in_miles=user_vehicle.is_mileage_in_miles,
		avg_fuel_consumption=_get_avg_fuel(user_vehicle),
		production_year=production_year,
		color=color,
		brand=brand,
		series=series,
		generation=generation,
		trim=trim,
		engine=engine,
		transmission=transmission,
	)


@cbv(user_vehicle_router)
class UserVehicleAPI(BaseAPI):
	"""API для управления транспортными средствами пользователя."""

	@user_vehicle_router.post(
		'/user-vehicles/',
		response_model=UserVehicleDetailSchema | UserVehicleWithChoicesSchema,
		summary='Добавить ТС в гараж',
	)
	async def create_by_vin(
		self,
		data: CreateUserVehicleByVinSchema,
	) -> UserVehicleDetailSchema | UserVehicleWithChoicesSchema:
		"""
		Добавить ТС в гараж по VIN-номеру.

		Если найдена одна комплектация — создает ТС сразу.
		Если несколько — возвращает варианты для выбора.
		"""
		vin_provider = CarInfoByVinProvider()
		car_info = vin_provider.get_info(data.vin)

		guess_service = GuessCommonCarInfo()
		guess_result = await guess_service.get_from_vin01(car_info)

		# Если одно поколение — создаем сразу
		if len(guess_result.generation) == 1:
			generation_id = guess_result.generation[0].id
			user_vehicle = await self._create_user_vehicle(
				user_id=str(self.user.id),
				generation_id=str(generation_id),
			)
			return UserVehicleDetailSchema(
				id=str(user_vehicle.id),
				vehicle_id=str(user_vehicle.vehicle_id) if user_vehicle.vehicle_id else None,
				user_id=str(user_vehicle.user_id),
				mileage=user_vehicle.mileage,
				is_mileage_in_miles=user_vehicle.is_mileage_in_miles,
				avg_fuel_consumption=_get_avg_fuel(user_vehicle),
				brand=guess_result.brand.name,
				series=guess_result.model.name,
				generation=guess_result.generation[0].name if guess_result.generation else None,
				trim=None,
				production_year=car_info.year,
				color=car_info.color,
			)

		# Несколько вариантов — возвращаем для выбора
		return UserVehicleWithChoicesSchema(
			choices=[
				UserVehicleChoiceSchema(
					brand=guess_result.brand,
					model=guess_result.model,
					generation=guess_result.generation,
					configuration=guess_result.configuration,
				),
			],
			vin=data.vin,
			year=car_info.year,
			color=car_info.color,
		)

	@user_vehicle_router.post(
		'/user-vehicles/by-choice/',
		response_model=UserVehicleDetailSchema,
		summary='Добавить ТС по выбранной комплектации',
	)
	async def create_by_choice(
		self,
		data: CreateUserVehicleByChoiceSchema,
	) -> UserVehicleDetailSchema:
		"""
		Создать ТС после выбора комплектации пользователем.
		"""
		user_vehicle = await self._create_user_vehicle(
			user_id=str(self.user.id),
			generation_id=data.generation_id,
		)

		return UserVehicleDetailSchema(
			id=str(user_vehicle.id),
			vehicle_id=str(user_vehicle.vehicle_id) if user_vehicle.vehicle_id else None,
			user_id=str(user_vehicle.user_id),
			mileage=user_vehicle.mileage,
			is_mileage_in_miles=user_vehicle.is_mileage_in_miles,
			avg_fuel_consumption=_get_avg_fuel(user_vehicle),
			brand=None,
			series=None,
			generation=None,
			trim=None,
			production_year=None,
			color=None,
		)

	@user_vehicle_router.post(
		'/user-vehicles/manual/',
		response_model=UserVehicleDetailSchema,
		summary='Добавить ТС вручную',
	)
	async def create_manual(
		self,
		data: CreateUserVehicleManualSchema,
	) -> UserVehicleDetailSchema:
		"""
		Добавить ТС в гараж вручную (без VIN).
		"""
		user_vehicle = await self._create_user_vehicle(
			user_id=str(self.user.id),
			generation_id=data.generation_id,
			trim_id=data.trim_id,
			mileage=data.mileage,
			is_mileage_in_miles=data.is_mileage_in_miles,
			avg_fuel_consumption=data.avg_fuel_consumption,
		)

		return UserVehicleDetailSchema(
			id=str(user_vehicle.id),
			vehicle_id=str(user_vehicle.vehicle_id) if user_vehicle.vehicle_id else None,
			user_id=str(user_vehicle.user_id),
			mileage=user_vehicle.mileage,
			is_mileage_in_miles=user_vehicle.is_mileage_in_miles,
			avg_fuel_consumption=_get_avg_fuel(user_vehicle),
			brand=None,
			series=None,
			generation=None,
			trim=None,
			production_year=data.production_year,
			color=data.color,
		)

	@user_vehicle_router.get(
		'/user-vehicles/',
		response_model=list[UserVehicleListSchema],
		summary='Получить список ТС пользователя',
	)
	async def list_user_vehicles(
		self,
	) -> list[UserVehicleListSchema]:
		"""
		Получить список всех транспортных средств текущего пользователя (минимальный набор данных).
		"""
		async with database.get_async_session() as session:
			stmt = (
				select(UserVehicle)
				.where(UserVehicle.user_id == self.user.id)
				.options(
					selectinload("generation").selectinload("series").selectinload("brand"),
				)
			)
			result = await session.execute(stmt)
			user_vehicles = result.scalars().unique().all()

		return [
			_build_user_vehicle_list_schema(uv) for uv in user_vehicles
		]

	@user_vehicle_router.get(
		'/user-vehicles/{user_vehicle_id}/',
		response_model=UserVehicleDetailFullSchema,
		summary='Детальная информация о ТС пользователя',
	)
	async def get_user_vehicle(
		self,
		user_vehicle_id: str,
	) -> UserVehicleDetailFullSchema:
		"""
		Получить детальную информацию о транспортном средстве пользователя.
		"""
		async with database.get_async_session() as session:
			stmt = (
				select(UserVehicle)
				.where(
					UserVehicle.id == UUID(user_vehicle_id),
					UserVehicle.user_id == self.user.id,
				)
				.options(
					selectinload("generation").selectinload("series").selectinload("brand"),
					selectinload("generation").selectinload("trims").selectinload("transmission"),
					selectinload("generation").selectinload("trims").selectinload("engine"),
					selectinload("vehicle"),
				)
			)
			result = await session.execute(stmt)
			user_vehicle = result.scalars().unique().one_or_none()

		if user_vehicle is None:
			from fastapi import HTTPException, status
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail='Транспортное средство не найдено',
			)

		return _build_user_vehicle_full_schema(user_vehicle)

	@staticmethod
	async def _create_user_vehicle(
		user_id: str,
		generation_id: str | None = None,
		trim_id: str | None = None,
		mileage: int | None = None,
		is_mileage_in_miles: bool = False,
		avg_fuel_consumption: float | None = None,
	) -> UserVehicle:
		"""
		Создать запись UserVehicle в БД.
		"""
		user_vehicle = UserVehicle(
			user_id=UUID(user_id),
			vehicle_id=None,
			generation_id=UUID(generation_id) if generation_id else None,
			trim_id=UUID(trim_id) if trim_id else None,
			mileage=mileage,
			is_mileage_in_miles=is_mileage_in_miles,
			avg_fuel_consumption=avg_fuel_consumption,
		)
		async with database.get_async_session() as session:
			session.add(user_vehicle)
			await session.commit()
			await session.refresh(user_vehicle)

		return user_vehicle
