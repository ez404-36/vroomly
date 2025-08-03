__all__ = (
    'get_list_countries',
)

from typing import List

from sqlalchemy import select

from apps.geo.api.routers import router
from apps.geo.api.schemas.readers import CountryDetail
from apps.geo.models.country import Country
from config.db import database


@router.get('/', response_model=List[CountryDetail])
async def get_list_countries():
    return await database.fetch_all(select(Country))
