from typing import Any, Iterable

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
    }
    default_data = {'vehicle_type': VehicleType.CAR}

    async def prefetch_data(self) -> dict[str, dict[Any, Any]]:
        brands: Iterable[VehicleBrand] = await session_fetch_all(self.session, select(VehicleBrand))
        mapped_brands = {
            brand.code: brand.id for brand in brands
        }

        return {
            'brands': mapped_brands
        }
