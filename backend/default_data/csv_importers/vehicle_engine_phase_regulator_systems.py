from typing import Any

from apps.vehicles.models.vehicle.vehicle_brand import VehicleBrand
from apps.vehicles.models.vehicle.vehicle_concern import VehicleConcern
from apps.vehicles.models.vehicle.vehicle_engine_phase_regulator_system import VehicleEnginePhaseRegulatorSystem
from .base import ImportObjectsFromCsvWithGenerateCode


class ImportVehicleEnginePhaseRegulatorSystemsCSV(ImportObjectsFromCsvWithGenerateCode):
    model = VehicleEnginePhaseRegulatorSystem
    source_filename = 'vehicle_engine_phase_regulator_system.csv'
    mapper = {
        'brand': 'brands:brand_id',
        'concern': 'concerns:concern_id',
    }
    code_from_fields = ('name',)

    async def prefetch_data(self) -> dict[str, dict[Any, Any]]:
        brands = await self.prefetch_objects(VehicleBrand)
        concerns = await self.prefetch_objects(VehicleConcern)

        return {
            'brands': {brand.code: brand.id for brand in brands},
            'concerns': {concern.code: concern.id for concern in concerns},
        }
