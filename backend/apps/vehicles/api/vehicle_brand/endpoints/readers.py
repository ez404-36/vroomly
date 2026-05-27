from typing import Annotated

from fastapi import Query
from fastapi_utils.cbv import cbv
from sqlalchemy import select

from apps.vehicles.api.routers import router
from apps.vehicles.api.vehicle_brand.filters import VehicleBrandFilterParams
from apps.vehicles.api.vehicle_brand.schemas.readers import VehicleBrandDetailSchema
from apps.vehicles.models.vehicle.vehicle_brand import VehicleBrand
from common.orm.filters import apply_search
from common.orm.views.mixins import BaseAPI
from core.db import database


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
		search_fields = ('code',)

		query = apply_search(
			select(VehicleBrand).order_by(filter_query.ordering),
			filter_query.search,
			search_fields,
		)

		if country := filter_query.country:
			query = query.filter(VehicleBrand.country_id == country.upper())

		return await database.fetch_all(query)
