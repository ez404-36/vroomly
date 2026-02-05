from typing import Any

from apps.vehicles.models.vehicle.vehicle_brand import VehicleBrand
from apps.vehicles.models.vehicle.vehicle_concern import VehicleConcern
from .base import ImportObjectsFromCsvWithGenerateCode


class ImportVehicleBrandsCSV(ImportObjectsFromCsvWithGenerateCode):
    model = VehicleBrand
    source_filename = 'vehicle_brand.csv'
    mapper = {
        'country': 'country_id',
        'concern': 'concerns:concern_id',
    }
    code_from_fields = ('abbreviation', 'name')

    async def prefetch_data(self) -> dict[str, dict[Any, Any]]:
        concerns = await self.prefetch_objects(VehicleConcern)

        return {
            'concerns': {concern.code: concern.id for concern in concerns}
        }
