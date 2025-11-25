from apps.vehicles.models.vehicle.vehicle_concern import VehicleConcern

from .base import ImportObjectsFromCsvWithGenerateCode


class ImportVehicleConcernsCSV(ImportObjectsFromCsvWithGenerateCode):
    model = VehicleConcern
    filename = 'vehicle_concern.csv'
    mapper = {
        'country': 'country_id',
    }
    code_from_fields = ('name',)
