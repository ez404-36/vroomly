"""Репозиторий доступа к данным ``UserVehicle`` (гараж пользователя)."""

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from apps.vehicles.models.car.car_spec import CarSpec
from apps.vehicles.models.car.car_trim import CarTrim
from apps.vehicles.models.vehicle.user_vehicle import UserVehicle
from apps.vehicles.models.vehicle.vehicle import Vehicle
from apps.vehicles.models.vehicle.vehicle_generation import VehicleGeneration
from apps.vehicles.models.vehicle.vehicle_series import VehicleSeries
from apps.vehicles.repositories.base import BaseRepository


def user_vehicle_detail_options() -> tuple[Any, ...]:
	"""
	``selectinload``-цепочка для загрузки всех связей Detail-схемы.

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


class UserVehicleRepository(BaseRepository[UserVehicle]):
	"""Доступ к ТС пользователя. Методы поиска возвращают объект или ``None``."""

	model = UserVehicle

	async def get_owned(self, user_vehicle_id: UUID, user_id: UUID) -> UserVehicle | None:
		"""
		Вернуть ТС, принадлежащее пользователю, или ``None``.

		Проверка владения — это фильтр ``user_id`` в запросе, а не выброс
		``HTTPException``: HTTP-семантика (404) остаётся в слое эндпоинтов.
		"""
		query = select(UserVehicle).where(
			UserVehicle.id == user_vehicle_id,
			UserVehicle.user_id == user_id,
		)
		return await self._fetch_one(query)

	async def get_owned_with_chain(self, user_vehicle_id: UUID, user_id: UUID) -> UserVehicle | None:
		"""Вернуть ТС пользователя с подгруженной цепочкой связей или ``None``."""
		query = (
			select(UserVehicle)
			.where(
				UserVehicle.id == user_vehicle_id,
				UserVehicle.user_id == user_id,
			)
			.options(*user_vehicle_detail_options())
		)
		return await self._fetch_one(query)

	async def get_with_chain(self, user_vehicle_id: UUID) -> UserVehicle | None:
		"""Вернуть ТС по id с подгруженной цепочкой связей (без проверки владения)."""
		query = (
			select(UserVehicle)
			.where(UserVehicle.id == user_vehicle_id)
			.options(*user_vehicle_detail_options())
		)
		return await self._fetch_one(query)

	async def list_for_user(self, user_id: UUID) -> list[UserVehicle]:
		"""Вернуть список ТС пользователя с подгруженными связями Detail-схемы."""
		query = (
			select(UserVehicle)
			.where(UserVehicle.user_id == user_id)
			.options(*user_vehicle_detail_options())
		)
		return await self._fetch_all(query)
