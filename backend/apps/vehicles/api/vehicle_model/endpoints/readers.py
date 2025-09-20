from typing import Annotated
from uuid import UUID

from apps.vehicles.api.routers import router
from apps.vehicles.api.vehicle_model.filters import VehicleModelFilterParams
from apps.vehicles.api.vehicle_model.schemas.readers import (
    VehicleModelDetail,
    VehicleModelList,
)
from apps.vehicles.models.vehicle_model import VehicleModel
from common.orm.filters import apply_search
from common.orm.views.mixins import BaseAPI
from core.db import database
from fastapi import Query
from fastapi_utils.cbv import cbv
from sqlalchemy import select
from sqlalchemy.orm import joinedload


@cbv(router)
class VehicleModelAPI(
    BaseAPI,
):

    @router.get(
        "/models/",
        response_model=list[VehicleModelList],
        summary="Список моделей",
    )
    async def list(self, filter_query: Annotated[VehicleModelFilterParams, Query()]):
        search_fields = ("name",)

        query = apply_search(
            select(VehicleModel).order_by(VehicleModel.name.asc()),
            filter_query.search,
            search_fields,
        )

        if brand := filter_query.brand:
            query = query.filter(VehicleModel.brand_id == brand)

        return await database.fetch_all(query)

    @router.get(
        "/models/{model_id}",
        response_model=VehicleModelDetail,
        summary="Детальный просмотр модели",
    )
    async def retrieve(self, model_id: UUID):
        query = (
            select(VehicleModel)
            .options(joinedload(VehicleModel.brand))
            .where(VehicleModel.id == model_id)
        )

        return await database.fetch_one(query)
