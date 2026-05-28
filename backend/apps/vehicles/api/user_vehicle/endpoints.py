from decimal import Decimal
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from fastapi_utils.cbv import cbv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from apps.vehicles.api.routers import user_vehicle_router
from apps.vehicles.api.user_vehicle.schemas import (
	CreateUserVehicleSchema,
	UpdateMileageSchema,
	UserVehicleDetailSchema,
	UserVehicleListSchema,
)
from apps.vehicles.models.car.car_spec import CarSpec
from apps.vehicles.models.car.car_trim import CarTrim
from apps.vehicles.models.vehicle.enums import VehicleType
from apps.vehicles.models.vehicle.user_vehicle import UserVehicle
from apps.vehicles.models.vehicle.vehicle import Vehicle
from apps.vehicles.models.vehicle.vehicle_generation import VehicleGeneration
from apps.vehicles.models.vehicle.vehicle_series import VehicleSeries
from common.orm.views.mixins import BaseAPI
from core.db import database


def _to_float(value: Any) -> float | None:
	"""Convert Decimal/None to float or return None."""
	if value is None:
		return None
	return float(value)


def _resolve_trim_chain(user_vehicle: UserVehicle) -> tuple[str | None, str | None, str | None, str | None]:
	"""
	Резолвит цепочку Brand → Series → Generation → Trim для уже загруженного UserVehicle.

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


def _user_vehicle_to_detail(user_vehicle: UserVehicle) -> UserVehicleDetailSchema:
	"""Конвертирует ORM UserVehicle (с подгруженными связями) в Detail-схему."""
	vehicle = user_vehicle.vehicle
	mileage = vehicle.mileage if vehicle is not None else None
	is_mileage_in_miles = vehicle.is_mileage_in_miles if vehicle is not None else False
	production_year = vehicle.production_year if vehicle is not None else None
	color = vehicle.color if vehicle is not None else None

	brand_name, series_name, generation_name, trim_name = _resolve_trim_chain(user_vehicle)

	return UserVehicleDetailSchema(
		id=str(user_vehicle.id),
		vehicle_id=str(user_vehicle.vehicle_id) if user_vehicle.vehicle_id else None,
		user_id=str(user_vehicle.user_id),
		mileage=mileage,
		is_mileage_in_miles=is_mileage_in_miles,
		avg_fuel_consumption=_to_float(user_vehicle.avg_fuel_consumption),
		brand=brand_name,
		series=series_name,
		generation=generation_name,
		trim=trim_name,
		production_year=production_year,
		color=color,
	)


def _user_vehicle_detail_options() -> tuple[Any, ...]:
	"""
	selectinload-цепочка для загрузки всех связей, нужных в Detail-схеме.

	``UserVehicle.vehicle → Vehicle.car_spec → CarSpec.trim → CarTrim.generation
	→ VehicleGeneration.series → VehicleSeries.brand``.
	"""
	return (
		selectinload(UserVehicle.vehicle)
		.selectinload(Vehicle.car_spec)
		.selectinload(CarSpec.trim)
		.selectinload(CarTrim.generation)
		.selectinload(VehicleGeneration.series)
		.selectinload(VehicleSeries.brand),
	)


@cbv(user_vehicle_router)
class UserVehicleAPI(BaseAPI):
	"""API для управления транспортными средствами пользователя."""

	@user_vehicle_router.post(
		'/user-vehicles/',
		response_model=UserVehicleDetailSchema,
		summary='Добавить ТС в гараж',
	)
	async def create_user_vehicle(
		self,
		data: CreateUserVehicleSchema,
	) -> UserVehicleDetailSchema:
		"""
		Создать ТС в гараже пользователя.

		Полностью «глупый» эндпоинт: использует строго присланные данные.
		Логика «угадай по VIN» вынесена в ``GET /vehicles/guess_by_vin``;
		фронт сам решает, какие поля передать после выбора пользователя.

		В одной транзакции создаются:

		- ``Vehicle`` (всегда; ``production_year`` обязателен по схеме);
		- ``CarSpec`` (только если переданы ``trim_id`` и ``vin``; vin NOT NULL на CarSpec);
		- ``UserVehicle`` (всегда, связан с Vehicle).
		"""
		trim_uuid = UUID(data.trim_id) if data.trim_id else None
		avg_fuel = Decimal(str(data.avg_fuel_consumption)) if data.avg_fuel_consumption is not None else None

		async with database.get_async_session() as session:
			vehicle = Vehicle(
				vehicle_type=VehicleType.CAR,
				production_year=data.production_year,
				color=data.color,
				mileage=data.mileage,
				is_mileage_in_miles=data.is_mileage_in_miles,
				country_id=None,
			)
			session.add(vehicle)
			await session.flush()

			if trim_uuid is not None and data.vin is not None:
				car_spec = CarSpec(
					vehicle_id=vehicle.id,
					trim_id=trim_uuid,
					vin=data.vin,
				)
				session.add(car_spec)
				await session.flush()

			user_vehicle = UserVehicle(
				user_id=self.user.id,
				vehicle_id=vehicle.id,
				avg_fuel_consumption=avg_fuel,
			)
			session.add(user_vehicle)
			await session.commit()

			loaded = await self._load_user_vehicle_with_chain(session, user_vehicle.id)

		if loaded is None:
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail='Не удалось загрузить созданное ТС',
			)
		return _user_vehicle_to_detail(loaded)

	@user_vehicle_router.get(
		'/user-vehicles/',
		response_model=list[UserVehicleListSchema],
		summary='Получить список ТС пользователя',
	)
	async def list_user_vehicles(
		self,
	) -> list[UserVehicleListSchema]:
		"""Получить список всех транспортных средств текущего пользователя."""
		query = (
			select(UserVehicle)
			.where(UserVehicle.user_id == self.user.id)
			.options(*_user_vehicle_detail_options())
		)
		return await database.fetch_all(query)

	@user_vehicle_router.get(
		'/user-vehicles/{user_vehicle_id}/',
		response_model=UserVehicleDetailSchema,
		summary='Детальная информация о ТС пользователя',
	)
	async def get_user_vehicle(
		self,
		user_vehicle_id: str,
	) -> UserVehicleDetailSchema:
		"""Получить детальную информацию о транспортном средстве пользователя."""
		query = (
			select(UserVehicle)
			.where(
				UserVehicle.id == UUID(user_vehicle_id),
				UserVehicle.user_id == self.user.id,
			)
			.options(*_user_vehicle_detail_options())
		)
		user_vehicle = await database.fetch_one(query)

		if user_vehicle is None:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail='Транспортное средство не найдено',
			)

		return _user_vehicle_to_detail(user_vehicle)

	@user_vehicle_router.patch(
		'/user-vehicles/{user_vehicle_id}/mileage/',
		response_model=UserVehicleDetailSchema,
		summary='Обновить пробег ТС пользователя',
	)
	async def update_user_vehicle_mileage(
		self,
		user_vehicle_id: str,
		data: UpdateMileageSchema,
	) -> UserVehicleDetailSchema:
		"""
		Обновить пробег транспортного средства пользователя.

		Пробег хранится на ``Vehicle`` (не на ``UserVehicle``), поэтому
		обновляется связанный ``Vehicle``. Доступно только владельцу ТС.
		"""
		async with database.get_async_session() as session:
			user_vehicle = await self._load_user_vehicle_with_chain(session, UUID(user_vehicle_id))

			if user_vehicle is None or user_vehicle.user_id != self.user.id:
				raise HTTPException(
					status_code=status.HTTP_404_NOT_FOUND,
					detail='Транспортное средство не найдено',
				)

			vehicle = user_vehicle.vehicle
			if vehicle is None:
				raise HTTPException(
					status_code=status.HTTP_404_NOT_FOUND,
					detail='У ТС отсутствует связанный объект транспортного средства',
				)

			vehicle.mileage = data.mileage
			vehicle.is_mileage_in_miles = data.is_mileage_in_miles
			await session.commit()

			loaded = await self._load_user_vehicle_with_chain(session, user_vehicle.id)

		if loaded is None:
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail='Не удалось загрузить обновлённое ТС',
			)
		return _user_vehicle_to_detail(loaded)

	@staticmethod
	async def _load_user_vehicle_with_chain(
		session: AsyncSession,
		user_vehicle_id: UUID,
	) -> UserVehicle | None:
		"""Загружает UserVehicle с подгруженной цепочкой Vehicle → CarSpec → CarTrim → ... → Brand."""
		query = (
			select(UserVehicle)
			.where(UserVehicle.id == user_vehicle_id)
			.options(*_user_vehicle_detail_options())
		)
		result = await session.scalars(query)
		return result.one_or_none()
