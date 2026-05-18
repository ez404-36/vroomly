from typing import Annotated
from uuid import UUID

from fastapi import Query
from fastapi_utils.cbv import cbv
from sqlalchemy import select

from apps.vehicles.api.routers import trim_router
from apps.vehicles.api.vehicle_trim.schemas.readers import VehicleTrimListSchema
from apps.vehicles.models.car.car_trim import CarTrim
from common.orm.views.mixins import BaseAPI
from core.db import database


@cbv(trim_router)
class VehicleTrimAPI(BaseAPI):
    @trim_router.get(
        '/',
        response_model=list[VehicleTrimListSchema],
        summary='Список комплектаций',
    )
    async def list(
        self,
        generation: Annotated[UUID | None, Query(description='ID поколения')] = None,
    ):
        query = select(CarTrim).order_by(CarTrim.name.asc())

        if generation:
            query = query.where(CarTrim.generation_id == generation)

        return await database.fetch_all(query)

    @trim_router.get(
        '/{trim_id}',
        response_model=VehicleTrimListSchema,
        summary='Детальный просмотр комплектации',
    )
    async def retrieve(self, trim_id: UUID):
        query = select(CarTrim).where(CarTrim.id == trim_id)
        return await database.fetch_one(query)