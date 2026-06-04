from typing import Annotated
from uuid import UUID

from fastapi import Query
from fastapi_utils.cbv import cbv

from apps.vehicles.api.routers import generation_router
from apps.vehicles.api.vehicle_generation.schemas.readers import (
	VehicleGenerationListSchema,
)
from apps.vehicles.repositories.vehicle_generation import VehicleGenerationRepository
from common.orm.views.mixins import BaseAPI


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
		return await VehicleGenerationRepository().list_for_series(series)

	@generation_router.get(
		'/{generation_id}',
		response_model=VehicleGenerationListSchema,
		summary='Детальный просмотр поколения',
	)
	async def retrieve(self, generation_id: UUID):
		return await VehicleGenerationRepository().get_by_id(generation_id)
