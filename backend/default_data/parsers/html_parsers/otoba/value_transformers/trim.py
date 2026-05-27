from decimal import Decimal
from typing import Any

from .base import OtobaRuValueBaseTransformer


class OtobaRuTrimValueTransformer(OtobaRuValueBaseTransformer):
	"""
	Парсит данные о комплектации автомобиля.
	"""

	int_fields = ('clearance',)
	fields_map = {
		'мощность мотора': 'power',
		'крутящий момент': 'torque',
		'разгон до 100 км/ч': 'acceleration',
		'макс. скорость': 'max_speed',
		'расход по городу': 'fuel_city',
		'расход по трассе': 'fuel_route',
		'смешанный расход': 'avg_fuel_consumption',
		'объем бензобака': 'fuel_tank',
		'снаряженная масса': 'weight',
		'полная масса': 'full_weight',
		'грузоподъемность': 'payload',
		'объем багажника': 'luggage_volume',
		'габаритная длина': 'length',
		'ширина': 'width',
		'высота': 'height',
		'колесная база': 'wheelbase',
		'клиренс': 'clearance',
		'кол-во дверей': 'doors',
		'кол-во мест': 'seats',
	}

	async def set_default_values(self, output: dict[str, Any]):
		if 'clearance' not in output:
			output['clearance'] = None

	async def parse_acceleration(self, value: str) -> dict[str, Any]:
		"""
		Разгон до 100 км/ч - парсим как Decimal
		"""
		from ..utils import find_first_number_in_text

		year = find_first_number_in_text(value)
		if year:
			return {'acceleration': Decimal(str(year / 10))}
		return {}

	async def parse_avg_fuel_consumption(self, value: str) -> dict[str, Any]:
		"""
		Средний расход топлива - парсим как Decimal
		"""
		from ..utils import find_first_number_in_text

		year = find_first_number_in_text(value)
		if year:
			return {'avg_fuel_consumption': Decimal(str(year / 10))}
		return {}
