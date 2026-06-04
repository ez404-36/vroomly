from fastapi_utils.cbv import cbv

from apps.geo.api.routers import router
from apps.geo.api.schemas.readers import CountryDetailSchema
from apps.geo.repositories.country import CountryRepository
from common.orm.views.mixins import BaseAPI


@cbv(router)
class CountryAPI(
	BaseAPI,
):
	@router.get(
		'/country/',
		response_model=list[CountryDetailSchema],
		summary='Список стран',
	)
	async def list(self):
		return await CountryRepository().list_all()
