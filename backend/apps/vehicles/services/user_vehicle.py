"""Бизнес-логика управления ТС пользователя (``UserVehicle``).

Сервис владеет транзакциями и инвариантами создания/обновления ТС. Он не знает
про HTTP: методы возвращают ORM-объект или ``None`` (например, при отсутствии
доступа/связи), а преобразование в HTTP-ответ — задача слоя эндпоинтов.
"""

from decimal import Decimal
from uuid import UUID

from apps.vehicles.api.user_vehicle.schemas import CreateUserVehicleSchema, UpdateMileageSchema
from apps.vehicles.models.car.car_spec import CarSpec
from apps.vehicles.models.vehicle.enums import VehicleType
from apps.vehicles.models.vehicle.user_vehicle import UserVehicle
from apps.vehicles.models.vehicle.vehicle import Vehicle
from apps.vehicles.repositories.user_vehicle import UserVehicleRepository
from core.db import database


class UserVehicleService:
	"""Создание ТС в гараже и обновление пробега."""

	async def create(self, data: CreateUserVehicleSchema, user_id: UUID) -> UserVehicle | None:
		"""
		Создать ТС в гараже пользователя в одной транзакции.

		Создаются:

		- ``Vehicle`` (всегда; ``production_year`` обязателен по схеме);
		- ``CarSpec`` (только если переданы ``trim_id`` и ``vin``; vin NOT NULL на CarSpec);
		- ``UserVehicle`` (всегда, связан с Vehicle).

		:returns: созданный ``UserVehicle`` с подгруженной цепочкой связей,
			либо ``None``, если его не удалось перечитать после коммита.
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
				user_id=user_id,
				vehicle_id=vehicle.id,
				avg_fuel_consumption=avg_fuel,
			)
			session.add(user_vehicle)
			await session.commit()

			repository = UserVehicleRepository(session)
			return await repository.get_with_chain(user_vehicle.id)

	async def update_mileage(
		self,
		user_vehicle_id: UUID,
		user_id: UUID,
		data: UpdateMileageSchema,
	) -> UserVehicle | None:
		"""
		Обновить пробег ТС пользователя.

		Пробег хранится на ``Vehicle`` (не на ``UserVehicle``), поэтому
		обновляется связанный ``Vehicle``. Доступно только владельцу ТС.

		:returns: обновлённый ``UserVehicle`` с подгруженной цепочкой связей;
			``None``, если ТС не принадлежит пользователю или у него нет ``Vehicle``.
		"""
		async with database.get_async_session() as session:
			repository = UserVehicleRepository(session)
			user_vehicle = await repository.get_owned_with_chain(user_vehicle_id, user_id)

			if user_vehicle is None:
				return None

			vehicle = user_vehicle.vehicle
			if vehicle is None:
				return None

			vehicle.mileage = data.mileage
			vehicle.is_mileage_in_miles = data.is_mileage_in_miles
			await session.commit()

			return await repository.get_with_chain(user_vehicle.id)
