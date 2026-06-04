from uuid import UUID

from fastapi_utils.cbv import cbv

from apps.vehicles.api.routers import vehicle_router
from apps.vehicles.api.vehicle.schemas.readers import VehicleDetailSchema
from apps.vehicles.models.vehicle.enums import VehicleType
from apps.vehicles.repositories.vehicle import VehicleRepository
from common.orm.views.mixins import BaseAPI
from common.schemas.choices_utils import enum_to_choices_list
from common.schemas.fields import ChoiceFieldSchema


@cbv(vehicle_router)
class VehicleAPI(
	BaseAPI,
):
	@vehicle_router.get(
		'/{vehicle_id}',
		response_model=VehicleDetailSchema,
		summary='Общая информация о ТС',
	)
	async def get_one(self, vehicle_id: UUID):
		return await VehicleRepository().get_by_id(vehicle_id)

	@vehicle_router.get(
		'/types/choices',
		response_model=list[ChoiceFieldSchema],
		summary='Список типов ТС',
	)
	async def get_vehicle_types_list(self):
		return enum_to_choices_list(VehicleType)
