import logging
from typing import Any

from sqlalchemy import and_, or_, select

from apps.vehicles.models.vehicle.enums import VehicleEngineGRMType, VehicleEngineType
from apps.vehicles.models.vehicle.vehicle_engine_phase_regulator_system import VehicleEnginePhaseRegulatorSystem
from common.utils.generators import generate_code
from core.db import database
from ..mappers import (
	grm_drive_type_mapper,
	phase_regulator_mapper,
    phase_regulator_system_mapper,
)
from .base import OtobaRuValueBaseTransformer


logger = logging.getLogger('OtobaRuEngineValueTransformer')


class OtobaRuEngineValueTransformer(OtobaRuValueBaseTransformer):
	int_fields = ('volume', 'power', 'cylinders', 'valves', 'torque')
	fields_map = {
		'точный объем': 'volume',
		'мощность двс': 'power',
		'мощность': 'power',
		'крутящий момент': 'torque',
		'блок цилиндров': 'cylinders',
		'кол-во цилиндров': 'cylinders',
		'головка блока': 'valves',
		'кол-во клапанов': 'valves',
		'привод грм': 'grm_drive_type',
		'фазорегулятор': 'phase_regulator',
		'экологич. класс': 'eco_class',
		'экологические нормы': 'eco_class',
		'тип топлива': 'type',
	}

	async def set_default_values(self, output: dict[str, Any]):
		output.setdefault('grm_drive_type', VehicleEngineGRMType.UNDEFINED)
		output.setdefault('type', VehicleEngineType.UNDEFINED)
		output.setdefault('volume', 0)

	async def parse_phase_regulator(self, value: str):
		"""
		Данные о фазорегуляторе.
		Если на найдено значение из enum, возвращается значение для phase_regulator_str
		"""
		output = {}

		if system_regular_type := phase_regulator_mapper.get(value.lower()):
			output['phase_regulator_type'] = system_regular_type
		else:
			as_bool = self.to_bool(value)
			if as_bool is None:
				value = (
					value.removeprefix('на впуске ')
					.replace('Dual ', 'D')
					.replace('dual ', 'D')
				)

				code = phase_regulator_system_mapper.get(value, generate_code(value))

				phase_regulator_system = await database.fetch_one(
					select(VehicleEnginePhaseRegulatorSystem).where(
						and_(
							or_(
								VehicleEnginePhaseRegulatorSystem.code == code,
								VehicleEnginePhaseRegulatorSystem.code == value,
							),
							self.brand_or_concern_condition(VehicleEnginePhaseRegulatorSystem)
						)

					)
				)

				if phase_regulator_system:
					output['phase_regulator_system_id'] = phase_regulator_system.id
				else:
					# Пытаемся найти регулятор фаз с таким же названием у другого Бренда
					other_brand_phase_regulator_system = await database.fetch_first(
						select(VehicleEnginePhaseRegulatorSystem).where(
								or_(
									VehicleEnginePhaseRegulatorSystem.code == code,
									VehicleEnginePhaseRegulatorSystem.code == value,
								)
						)
					)
					if other_brand_phase_regulator_system:
						output['phase_regulator_system_id'] = other_brand_phase_regulator_system.id
					else:
						logger.warning(f'Не опознан тип регулирования фаз странице {self.page_uri}: {value}')

		return output

	async def parse_grm_drive_type(self, value: str):
		output = {}

		if grm_drive_type := grm_drive_type_mapper.get(value.lower()):
			output['grm_drive_type'] = grm_drive_type
		else:
			logger.warning(f'Не опознан привод ГРМ на странице {self.page_uri}: {value}')

		return output

	async def parse_type(self, value: str):
		"""
		Определяет тип двигателя по Типу топлива :)
		"""
		output = {}
		value = value.lower()

		if 'аи' in value:
			engine_type = VehicleEngineType.PETROL
		elif 'дизел' in value:
			engine_type = VehicleEngineType.DIESEL
		elif value in ['метан', 'пропан-бутан']:
			engine_type = VehicleEngineType.GAS
		else:
			logger.warning(f'Не удалось определить тип двигателя по топливу на странице {self.page_uri}: {value}')
			engine_type = VehicleEngineType.PETROL

		has_turbo = self.to_bool(self.tags_data.get('турбонаддув'))
		if has_turbo:
			engine_type |= VehicleEngineType.TURBO
		else:
			engine_type |= VehicleEngineType.ATMOSPHERIC

		output['type'] = engine_type

		return output
