from uuid import UUID

from fastapi_utils.cbv import cbv
from sqlalchemy import select

from apps.vehicles.api.routers import router
from apps.vehicles.api.vehicle.schemas.readers import VehicleDetailSchema
from apps.vehicles.models.vehicle.vehicle import Vehicle
from common.orm.views.mixins import BaseAPI
from core.db import database


@cbv(router)
class VehicleAPI(
    BaseAPI,
):
    @router.get(
        "/vehicle/{vehicle_id}",
        response_model=VehicleDetailSchema,
        summary="Общая информация о ТС",
    )
    async def retrieve(self, vehicle_id: UUID):
        query = (
            select(Vehicle)
            .where(Vehicle.id == vehicle_id)
        )

        return await database.fetch_one(query)
