from apps.vehicles.models.node.engine_node import EngineNode
from default_data.csv_importers.base import ImportJTINodesFromCSVBase


class ImportVehicleEnginesCSV(ImportJTINodesFromCSVBase):
	"""
	Импорт двигателей (JTI-узел ``EngineNode``)
	"""

	model = EngineNode
	source_filename = 'engine_node.csv'
