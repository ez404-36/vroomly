from apps.vehicles.models.vehicle_brand import VehicleBrand

from .base import ImportFromCSVBase


class ImportVehicleBrandsCSV(ImportFromCSVBase):
    model = VehicleBrand
    filename = 'vehicle_brand.csv'
    mapper = {
        'country': 'country_id',
    }
