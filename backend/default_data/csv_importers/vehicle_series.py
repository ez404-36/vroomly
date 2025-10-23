from typing import Any, Iterable

from apps.vehicles.models.vehicle.enums import VehicleType
from sqlalchemy import select

from apps.vehicles.models.vehicle.vehicle_brand import VehicleBrand
from apps.vehicles.models.vehicle.vehicle_series import VehicleSeries
from core.db import database
from .base import ImportFromCSVBase


class ImportVehicleSeriesCSV(ImportFromCSVBase):
    model = VehicleSeries
    filename = 'vehicle_series.csv'
    mapper = {
        'brand': 'brands:brand_id',
    }
    default_data = {'vehicle_type': VehicleType.CAR}

    async def prefetch_data(self) -> dict[str, dict[Any, Any]]:
        brands: Iterable[VehicleBrand] = await database.session_fetch_all(
            self.session, select(VehicleBrand)
        )
        mapped = {brand.code: brand.id for brand in brands}

        return {'brands': mapped}
