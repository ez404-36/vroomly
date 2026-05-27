from apps.vehicles.models.vehicle.vehicle_brand import VehicleBrand

from .base import ImportObjectsFromCsvWithGenerateCode


class ImportVehicleBrandsCSV(ImportObjectsFromCsvWithGenerateCode):
	"""
	Импорт марок автомобилей
	"""

	model = VehicleBrand
	source_filename = 'vehicle_brand.csv'
