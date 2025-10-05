from typing import Annotated
from uuid import UUID

from apps.vehicles.api.routers import router
from apps.vehicles.api.vehicle_series.filters import VehicleSeriesFilterParams
from apps.vehicles.api.vehicle_series.schemas.readers import (
    VehicleSeriesDetailSchema,
    VehicleSeriesListSchema,
)
from apps.vehicles.models.vehicle.vehicle_series import VehicleSeries
from common.orm.filters import apply_search
from common.orm.views.mixins import BaseAPI
from core.db import database
from fastapi import Query
from fastapi_utils.cbv import cbv
from sqlalchemy import select
from sqlalchemy.orm import joinedload


@cbv(router)
class VehicleSeriesAPI(
    BaseAPI,
):

    @router.get(
        "/series/",
        response_model=list[VehicleSeriesListSchema],
        summary="Список моделей",
    )
    async def list(self, filter_query: Annotated[VehicleSeriesFilterParams, Query()]):
        search_fields = ("name",)

        query = apply_search(
            select(VehicleSeries).order_by(VehicleSeries.name.asc()),
            filter_query.search,
            search_fields,
        )

        if brand := filter_query.brand:
            query = query.filter(VehicleSeries.brand_id == brand)

        return await database.fetch_all(query)

    @router.get(
        "/series/{series_id}",
        response_model=VehicleSeriesDetailSchema,
        summary="Детальный просмотр модели",
    )
    async def retrieve(self, series_id: UUID):
        query = (
            select(VehicleSeries)
            .options(joinedload(VehicleSeries.brand))
            .where(VehicleSeries.id == series_id)
        )

        return await database.fetch_one(query)
