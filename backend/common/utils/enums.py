"""
Mapping utilities for vehicle enums.
"""


class CarDriveType:
	"""Mapping for CarDriveType enum values."""

	FRONT = 1
	BACK = 2
	FULL = 3

	@classmethod
	def to_label(cls, value: int | None) -> str | None:
		if value is None:
			return None
		mapping = {cls.FRONT: 'Передний', cls.BACK: 'Задний', cls.FULL: 'Полный'}
		return mapping.get(value)


class VehicleTransmissionType:
	"""Mapping for VehicleTransmissionType enum values."""

	MANUAL = 1
	AUTO = 2
	ROBOT = 3
	VARIATOR = 4

	@classmethod
	def to_label(cls, value: int | None) -> str | None:
		if value is None:
			return None
		mapping = {
			cls.MANUAL: 'Механика',
			cls.AUTO: 'Автомат',
			cls.ROBOT: 'Робот',
			cls.VARIATOR: 'Вариатор',
		}
		return mapping.get(value, 'Не определено')


class EngineTypeBitmask:
	"""Mapping for VehicleEngineType bitmask values."""

	PETROL = 1
	DIESEL = 2
	ELECTRO = 4
	GAS = 8
	ATMOSPHERIC = 16
	TURBO = 32

	@classmethod
	def to_labels(cls, value: int | None) -> list[str]:
		if value is None or value == 0:
			return []
		labels = []
		if value & cls.PETROL:
			labels.append('Бензиновый')
		if value & cls.DIESEL:
			labels.append('Дизельный')
		if value & cls.ELECTRO:
			labels.append('Электрический')
		if value & cls.GAS:
			labels.append('Газовый')
		if value & cls.ATMOSPHERIC:
			labels.append('Атмосферный')
		if value & cls.TURBO:
			labels.append('Турбированный')
		return labels


class GRMTypeBitmask:
	"""Mapping for VehicleEngineGRMType bitmask values."""

	BELT = 1
	CHAIN = 2
	GEARS = 4
	WET_BELT = 64
	TWO_CHAINS = 8
	TWO_BELTS = 128

	@classmethod
	def to_labels(cls, value: int | None) -> list[str]:
		if value is None or value == 0:
			return []
		labels = []
		if value & cls.BELT:
			labels.append('Ремень')
		if value & cls.CHAIN:
			labels.append('Цепь')
		if value & cls.GEARS:
			labels.append('Шестерни')
		if value & cls.WET_BELT:
			labels.append('Мокрый ремень')
		if value & cls.TWO_CHAINS:
			labels.append('2 цепи')
		if value & cls.TWO_BELTS:
			labels.append('2 ремня')
		return labels


class PhaseRegulatorType:
	"""Mapping for VehicleEnginePhaseRegulatorType enum values."""

	INPUT = 1
	OUTPUT = 2
	DUAL = 3
	COMPLEX = 4

	@classmethod
	def to_label(cls, value: int | None) -> str | None:
		if value is None:
			return None
		mapping = {
			cls.INPUT: 'На впуске',
			cls.OUTPUT: 'На выпуске',
			cls.DUAL: 'На обоих валах',
			cls.COMPLEX: 'Сложная',
		}
		return mapping.get(value)
