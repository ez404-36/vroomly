from apps.vehicles.models.vehicle_brand import VehicleBrand
from default_data.import_from_csv_base import ImportFromCSVBase


class ImportVehicleBrandsCSV(ImportFromCSVBase):
    model = VehicleBrand
    filename = 'vehicle_brand.csv'
    mapper = {
        'country': 'country_id',
        'brand': 'name',
    }
