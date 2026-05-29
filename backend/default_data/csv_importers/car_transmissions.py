from apps.vehicles.models.node.transmission_node import CarTransmissionNode
from default_data.csv_importers.base import ImportJTINodesFromCSVBase


class ImportCarTransmissionsCSV(ImportJTINodesFromCSVBase):
	"""
	Импорт коробок передач автомобилей (JTI-узел ``CarTransmissionNode``)
	"""

	model = CarTransmissionNode
	source_filename = 'car_transmission_node.csv'

	def transform_object_data(self, instance_data: dict) -> dict:
		"""
		Преобразование данных строки CSV перед вставкой в БД.

		Поле ``drive_types`` в CSV хранится в нотации PostgreSQL-массива
		(например, ``{2,3}``). Базовый класс импорта оставляет его строкой,
		а ``IntEnumArrayType`` ожидает Python-итерируемое целых чисел —
		преобразуем здесь.
		"""
		instance_data = super().transform_object_data(instance_data)

		raw_drive_types = instance_data.get('drive_types')
		instance_data['drive_types'] = self._parse_int_array(raw_drive_types)

		return instance_data

	@staticmethod
	def _parse_int_array(value: str | None) -> list[int]:
		"""Парсит PostgreSQL-нотацию массива ``{1,2,3}`` в ``list[int]``."""
		if not value:
			return []
		inner = value.strip().strip('{}')
		if not inner:
			return []
		return [int(part) for part in inner.split(',') if part.strip()]
