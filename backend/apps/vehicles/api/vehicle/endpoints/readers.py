from uuid import UUID

from fastapi_utils.cbv import cbv
from sqlalchemy import select

from apps.vehicles.api.routers import vehicle_router
from apps.vehicles.api.vehicle.schemas.readers import VehicleDetailSchema
from apps.vehicles.models.vehicle.enums import VehicleType
from apps.vehicles.models.vehicle.vehicle import Vehicle
from common.orm.views.mixins import BaseAPI
from common.schemas.choices_utils import enum_to_choices_list
from common.schemas.fields import ChoiceFieldSchema
from core.db import database


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
		query = select(Vehicle).where(Vehicle.id == vehicle_id)

		return await database.fetch_one(query)

	@vehicle_router.get(
		'/types/choices',
		response_model=list[ChoiceFieldSchema],
		summary='Список типов ТС',
	)
	async def get_vehicle_types_list(self):
		return enum_to_choices_list(VehicleType)
