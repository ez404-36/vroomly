from apps.vehicles.models.vehicle.vehicle_series import VehicleSeries

from .base import ImportObjectsFromCSVBase


class ImportVehicleSeriesCSV(ImportObjectsFromCSVBase):
    """
    Импорт моделей автомобилей
    """

    model = VehicleSeries
    source_filename = 'vehicle_series.csv'
