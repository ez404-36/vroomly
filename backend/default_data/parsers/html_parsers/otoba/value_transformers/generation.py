from typing import Any

from ..utils import find_first_number_in_text
from .base import OtobaRuValueBaseTransformer


class OtobaRuGenerationValueTransformer(OtobaRuValueBaseTransformer):
	"""
	Парсит данные о поколении модели ТС.
	"""
	int_fields = ('start_year', 'end_year')
	fields_map = {
		'начало продаж': 'start_year',
		'год начала': 'start_year',
		'конец продаж': 'end_year',
		'год окончания': 'end_year',
	}

	async def set_default_values(self, output: dict[str, Any]):
		if 'start_year' not in output:
			output['start_year'] = 0
		if 'end_year' not in output:
			output['end_year'] = None

	async def parse_start_year(self, value: str) -> dict[str, Any]:
		return {'start_year': find_first_number_in_text(value)}

	async def parse_end_year(self, value: str) -> dict[str, Any]:
		year = find_first_number_in_text(value)
		if year and year > 2100:
			return {'end_year': None}
		return {'end_year': year if year else None}