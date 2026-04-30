from apps.vehicles.models.vehicle.vehicle_engine import VehicleEngine
from default_data.csv_importers.base import ImportObjectsFromCSVBase


class ImportVehicleEnginesCSV(ImportObjectsFromCSVBase):
    """
    Импорт двигателей
    """

    model = VehicleEngine
    source_filename = 'vehicle_engine.csv'
