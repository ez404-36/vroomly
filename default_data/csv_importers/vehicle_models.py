from typing import Any

from sqlalchemy import select

from apps.vehicles.models.vehicle_brand import VehicleBrand
from apps.vehicles.models.vehicle_model import VehicleModel, VehicleType
from core.db import session_fetch_all

from .base import ImportFromCSVBase


class ImportVehicleModelsCSV(ImportFromCSVBase):
    model = VehicleModel
    filename = 'vehicle_model.csv'
    mapper = {
        'brand': 'brands:brand_id',
        'model': 'name',
    }
    default_data = {'vehicle_type': VehicleType.CAR}

    async def prefetch_data(self) -> dict[str, dict[Any, Any]]:
        brands = await session_fetch_all(self.session, select(VehicleBrand))
        mapped_brands = {
            brand.name.upper().replace(' ', '_'): brand for brand in brands
        }

        return {
            'brands': mapped_brands
        }
