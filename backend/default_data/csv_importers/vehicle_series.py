from typing import Any

from apps.vehicles.models.vehicle.enums import VehicleType
from apps.vehicles.models.vehicle.vehicle_brand import VehicleBrand
from apps.vehicles.models.vehicle.vehicle_series import VehicleSeries
from .base import ImportObjectsFromCSVBase


class ImportVehicleSeriesCSV(ImportObjectsFromCSVBase):
    model = VehicleSeries
    filename = 'vehicle_series.csv'
    mapper = {
        'brand': 'brands:brand_id',
    }
    default_data = {'vehicle_type': VehicleType.CAR}

    async def prefetch_data(self) -> dict[str, dict[Any, Any]]:
        brands = await self.prefetch_objects(VehicleBrand)

        return {
            'brands': {brand.code: brand.id for brand in brands},
        }
