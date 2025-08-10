from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from apps.geo.models.country import Country
from apps.vehicles.models.vehicle_brand import VehicleBrand
from config.db import session_fetch_all
from default_data.import_from_csv_base import ImportFromCSVBase


class ImportVehicleBrandsCSV(ImportFromCSVBase):
    model = VehicleBrand
    filename = 'vehicle_brand.csv'
    mapper = {
        'country': 'country_id:country.prefix',
        'brand': 'name',
    }

    @classmethod
    async def prefetch_data(cls, session: Session | AsyncSession):
        countries = await session_fetch_all(session, select(Country))
        return {
            'country': {
                country.prefix: country.id
                for country in countries
            }
        }
