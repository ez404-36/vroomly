from typing import Any

from ..utils import find_first_number_in_text
from .base import OtobaRuValueBaseTransformer

# Верхняя граница допустимого года выпуска (совпадает с CHECK на vehicle_generation).
_MAX_PRODUCTION_YEAR = 2100


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
		"""Заполняет недостающие ключи значениями по умолчанию."""
		if 'start_year' not in output:
			output['start_year'] = 0
		if 'end_year' not in output:
			output['end_year'] = None

	async def parse_start_year(self, value: str) -> dict[str, Any]:
		"""Извлекает год начала продаж из текстового значения."""
		return {'start_year': find_first_number_in_text(value)}

	async def parse_end_year(self, value: str) -> dict[str, Any]:
		"""Извлекает год окончания продаж, отсекая нереалистично большие значения."""
		year = find_first_number_in_text(value)
		if year and year > _MAX_PRODUCTION_YEAR:
			return {'end_year': None}
		return {'end_year': year if year else None}
