__all__ = (
    'get_list_countries',
)

from sqlalchemy import select

from apps.geo.api.routers import router
from apps.geo.api.schemas.readers import CountryDetail
from apps.geo.models.country import Country
from core.db import database


@router.get('/country/', response_model=list[CountryDetail])
async def get_list_countries():
    return await database.fetch_all(select(Country))
