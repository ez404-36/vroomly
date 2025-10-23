from apps.vehicles.models.vehicle.vehicle_concern import VehicleConcern
from common.utils.generators import generate_code

from .base import ImportFromCSVBase


class ImportVehicleConcernsCSV(ImportFromCSVBase):
    model = VehicleConcern
    filename = 'vehicle_concern.csv'
    mapper = {
        'country': 'country_id',
    }

    def transform_object_data(self, instance_data: dict) -> dict:
        if not instance_data.get('code'):
            instance_data['code'] = generate_code(instance_data.get('name'))

        return instance_data
