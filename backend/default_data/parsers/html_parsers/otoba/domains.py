from typing import Literal


class OtobaRuError(Exception):
	"""Ошибка работы otoba-парсера."""


VehicleNodeType = Literal['engine', 'transmission', 'vehicle', 'china_vehicle']
NUMBER_PATTERN = r'\d+'
