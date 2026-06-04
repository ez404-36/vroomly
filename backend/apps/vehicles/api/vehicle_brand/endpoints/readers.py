from typing import Annotated

from fastapi import Query
from fastapi_utils.cbv import cbv

from apps.vehicles.api.routers import router
from apps.vehicles.api.vehicle_brand.filters import VehicleBrandFilterParams
from apps.vehicles.api.vehicle_brand.schemas.readers import VehicleBrandDetailSchema
from apps.vehicles.repositories.vehicle_brand import VehicleBrandRepository
from common.orm.views.mixins import BaseAPI


@cbv(router)
class BrandAPI(
	BaseAPI,
):
	@router.get(
		'/brands/',
		response_model=list[VehicleBrandDetailSchema],
		summary='Список марок',
	)
	async def list(self, filter_query: Annotated[VehicleBrandFilterParams, Query()]):
		return await VehicleBrandRepository().list_filtered(
			ordering=filter_query.ordering,
			search=filter_query.search,
			country=filter_query.country,
		)
