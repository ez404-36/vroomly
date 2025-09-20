from apps.geo.api.routers import router
from apps.geo.api.schemas.readers import CountryDetail
from apps.geo.models.country import Country
from common.orm.views.mixins import BaseAPI
from core.db import database
from fastapi_utils.cbv import cbv
from sqlalchemy import select


@cbv(router)
class CountryAPI(
    BaseAPI,
):
    @router.get(
        "/country/",
        response_model=list[CountryDetail],
        summary="Список стран",
    )
    async def list(self):
        return await database.fetch_all(select(Country))
