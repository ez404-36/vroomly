from apps.vehicles.models.vehicle.vehicle_concern import VehicleConcern

from .base import ImportObjectsFromCsvWithGenerateCode


class ImportVehicleConcernsCSV(ImportObjectsFromCsvWithGenerateCode):
	"""
	Импорт автомобильных концернов
	"""

	model = VehicleConcern
	source_filename = 'vehicle_concern.csv'
