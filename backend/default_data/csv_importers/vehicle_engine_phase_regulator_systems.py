from apps.vehicles.models.vehicle.vehicle_engine_phase_regulator_system import VehicleEnginePhaseRegulatorSystem

from .base import ImportObjectsFromCsvWithGenerateCode


class ImportVehicleEnginePhaseRegulatorSystemsCSV(ImportObjectsFromCsvWithGenerateCode):
	"""
	Импорт систем фазорегулирования
	"""

	model = VehicleEnginePhaseRegulatorSystem
	source_filename = 'vehicle_engine_phase_regulator_system.csv'
