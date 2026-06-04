from uuid import UUID

from fastapi import HTTPException, status
from fastapi_utils.cbv import cbv

from apps.vehicles.api.routers import user_vehicle_router
from apps.vehicles.api.user_vehicle.mappers import user_vehicle_to_detail, user_vehicles_to_list
from apps.vehicles.api.user_vehicle.schemas import (
	CreateUserVehicleSchema,
	UpdateMileageSchema,
	UserVehicleDetailSchema,
	UserVehicleListSchema,
)
from apps.vehicles.repositories.user_vehicle import UserVehicleRepository
from apps.vehicles.services.user_vehicle import UserVehicleService
from common.orm.views.mixins import BaseAPI

_NOT_FOUND = 'Транспортное средство не найдено'


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

		Логика «угадай по VIN» вынесена в ``GET /vehicles/guess_by_vin``;
		фронт сам решает, какие поля передать после выбора пользователя.
		"""
		user_vehicle = await UserVehicleService().create(data, self.user.id)
		if user_vehicle is None:
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail='Не удалось загрузить созданное ТС',
			)
		return user_vehicle_to_detail(user_vehicle)

	@user_vehicle_router.get(
		'/user-vehicles/',
		response_model=list[UserVehicleListSchema],
		summary='Получить список ТС пользователя',
	)
	async def list_user_vehicles(self) -> list[UserVehicleListSchema]:
		"""Получить список всех транспортных средств текущего пользователя."""
		user_vehicles = await UserVehicleRepository().list_for_user(self.user.id)
		return user_vehicles_to_list(user_vehicles)

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
		user_vehicle = await UserVehicleRepository().get_owned_with_chain(
			UUID(user_vehicle_id),
			self.user.id,
		)
		if user_vehicle is None:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=_NOT_FOUND)
		return user_vehicle_to_detail(user_vehicle)

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
		"""Обновить пробег транспортного средства пользователя (доступно владельцу)."""
		user_vehicle = await UserVehicleService().update_mileage(
			UUID(user_vehicle_id),
			self.user.id,
			data,
		)
		if user_vehicle is None:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=_NOT_FOUND)
		return user_vehicle_to_detail(user_vehicle)
