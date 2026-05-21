from typing import Annotated
from uuid import UUID

from fastapi import Query
from fastapi_utils.cbv import cbv
from sqlalchemy import select

from apps.vehicles.api.routers import generation_router
from apps.vehicles.api.vehicle_generation.schemas.readers import (
    VehicleGenerationListSchema,
)
from apps.vehicles.models.vehicle.vehicle_generation import VehicleGeneration
from common.orm.views.mixins import BaseAPI
from core.db import database


@cbv(generation_router)
class VehicleGenerationAPI(BaseAPI):
    @generation_router.get(
        '/',
        response_model=list[VehicleGenerationListSchema],
        summary='Список поколений',
    )
    async def list(
        self,
        series: Annotated[UUID | None, Query(description='ID серии')] = None,
    ):
        query = select(VehicleGeneration).order_by(VehicleGeneration.start_year.desc())

        if series:
            query = query.where(VehicleGeneration.series_id == series)

        return await database.fetch_all(query)

    @generation_router.get(
        '/{generation_id}',
        response_model=VehicleGenerationListSchema,
        summary='Детальный просмотр поколения',
    )
    async def retrieve(self, generation_id: UUID):
        query = select(VehicleGeneration).where(VehicleGeneration.id == generation_id)
        return await database.fetch_one(query)