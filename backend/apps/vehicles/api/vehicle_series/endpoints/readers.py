from typing import Annotated
from uuid import UUID

from fastapi import Query
from fastapi_utils.cbv import cbv

from apps.vehicles.api.routers import series_router
from apps.vehicles.api.vehicle_series.filters import VehicleSeriesFilterParams
from apps.vehicles.api.vehicle_series.schemas.readers import (
	VehicleSeriesDetailSchema,
	VehicleSeriesListSchema,
)
from apps.vehicles.repositories.vehicle_series import VehicleSeriesRepository
from common.orm.views.mixins import BaseAPI


@cbv(series_router)
class VehicleSeriesAPI(
	BaseAPI,
):
	@series_router.get(
		'/',
		response_model=list[VehicleSeriesListSchema],
		summary='Список моделей',
	)
	async def list(self, filter_query: Annotated[VehicleSeriesFilterParams, Query()]):
		return await VehicleSeriesRepository().list_filtered(
			brand_id=filter_query.brand,
			search=filter_query.search,
		)

	@series_router.get(
		'/{series_id}',
		response_model=VehicleSeriesDetailSchema,
		summary='Детальный просмотр модели',
	)
	async def retrieve(self, series_id: UUID):
		return await VehicleSeriesRepository().get_with_brand(series_id)
