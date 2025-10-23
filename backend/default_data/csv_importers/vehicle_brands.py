from typing import Any, Iterable

from sqlalchemy import select

from apps.vehicles.models.vehicle.vehicle_brand import VehicleBrand
from apps.vehicles.models.vehicle.vehicle_concern import VehicleConcern
from common.utils.generators import generate_code
from core.db import database
from .base import ImportFromCSVBase


class ImportVehicleBrandsCSV(ImportFromCSVBase):
    model = VehicleBrand
    filename = 'vehicle_brand.csv'
    mapper = {
        'country': 'country_id',
        'concern': 'concerns:concern_id',
    }

    def transform_object_data(self, instance_data: dict) -> dict:
        if not instance_data.get('code'):
            abbreviation = instance_data.get('abbreviation')
            name = instance_data.get('name')
            instance_data['code'] = generate_code(abbreviation or name)

        return instance_data

    async def prefetch_data(self) -> dict[str, dict[Any, Any]]:
        concerns: Iterable[VehicleConcern] = await database.session_fetch_all(
            self.session, select(VehicleConcern)
        )
        mapped = {concern.code: concern.id for concern in concerns}

        return {'concerns': mapped}
