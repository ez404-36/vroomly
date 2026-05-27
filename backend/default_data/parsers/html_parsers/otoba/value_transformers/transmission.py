import logging
from typing import Any

from apps.vehicles.models.car.enums import CarDriveType
from apps.vehicles.models.vehicle.enums import VehicleTransmissionType

from ..mappers import transmission_drive_type_mapper, transmission_type_mapper
from .base import OtobaRuValueBaseTransformer

logger = logging.getLogger('OtobaRuTransmissionValueTransformer')


class OtobaRuTransmissionValueTransformer(OtobaRuValueBaseTransformer):
	int_fields = ('gears',)
	fields_map = {
		'тип': 'type',
		'количество передач': 'gears',
		'крутящий момент': 'torque',
		'для привода': 'drive_types',
	}

	async def set_default_values(self, output: dict[str, Any]):
		if not output.get('gears'):
			output['gears'] = 0

	async def parse_type(self, value: str):
		output = {}

		if t_type := transmission_type_mapper.get(value.lower()):
			output['type'] = t_type
			if t_type == VehicleTransmissionType.VARIATOR:
				output['gears'] = 0
		else:
			logger.warning(f'Не опознан тип коробки передач на странице {self.page_uri}: {value}')

		return output

	async def parse_drive_types(self, value: str):
		drive_types: list[CarDriveType] = []

		if '/' in value:
			values = value.split('/')
		elif ',' in value:
			values = value.split(',')
		elif '+' in value:
			values = value.split('+')
		elif value == 'любой':
			values = [
				CarDriveType.FRONT,
				CarDriveType.BACK,
				CarDriveType.FULL,
			]
		else:
			values = [value]

		for val in values:
			if isinstance(val, str):
				drive_type = transmission_drive_type_mapper.get(val.strip().lower())
			else:
				drive_type = val

			if drive_type:
				drive_types.append(drive_type)
			else:
				logger.warning(f'Не опознан тип привода на странице {self.page_uri}: {value} ({val})')

		return {
			'drive_types': drive_types,
		}
