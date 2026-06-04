from typing import Annotated
from uuid import UUID

from fastapi import Query
from fastapi_utils.cbv import cbv

from apps.vehicles.api.routers import trim_router
from apps.vehicles.api.vehicle_trim.schemas.readers import VehicleTrimListSchema
from apps.vehicles.repositories.car_trim import CarTrimRepository
from common.orm.views.mixins import BaseAPI


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
		return await CarTrimRepository().list_for_generation(generation)

	@trim_router.get(
		'/{trim_id}',
		response_model=VehicleTrimListSchema,
		summary='Детальный просмотр комплектации',
	)
	async def retrieve(self, trim_id: UUID):
		return await CarTrimRepository().get_by_id(trim_id)
