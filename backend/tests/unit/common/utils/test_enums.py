"""Tests for vehicle enum mappings in common/utils/enums.py."""

from common.utils.enums import (
	CarDriveType,
	EngineTypeBitmask,
	GRMTypeBitmask,
	PhaseRegulatorType,
	VehicleTransmissionType,
)


class TestCarDriveTypeMapping:
	"""Tests for CarDriveType mapping."""

	def test_to_label_front(self):
		"""Should return 'Передний' for FRONT."""
		assert CarDriveType.to_label(1) == 'Передний'

	def test_to_label_back(self):
		"""Should return 'Задний' for BACK."""
		assert CarDriveType.to_label(2) == 'Задний'

	def test_to_label_full(self):
		"""Should return 'Полный' for FULL."""
		assert CarDriveType.to_label(3) == 'Полный'

	def test_to_label_none(self):
		"""Should return None for None."""
		assert CarDriveType.to_label(None) is None


class TestVehicleTransmissionTypeMapping:
	"""Tests for VehicleTransmissionType mapping."""

	def test_to_label_manual(self):
		"""Should return 'Механика' for MANUAL."""
		assert VehicleTransmissionType.to_label(1) == 'Механика'

	def test_to_label_auto(self):
		"""Should return 'Автомат' for AUTO."""
		assert VehicleTransmissionType.to_label(2) == 'Автомат'

	def test_to_label_robot(self):
		"""Should return 'Робот' for ROBOT."""
		assert VehicleTransmissionType.to_label(3) == 'Робот'

	def test_to_label_variator(self):
		"""Should return 'Вариатор' for VARIATOR."""
		assert VehicleTransmissionType.to_label(4) == 'Вариатор'

	def test_to_label_undefined(self):
		"""Should return 'Не определено' for unknown value."""
		assert VehicleTransmissionType.to_label(0) == 'Не определено'


class TestEngineTypeBitmaskMapping:
	"""Tests for EngineTypeBitmask mapping."""

	def test_petrol(self):
		"""Should detect PETROL flag."""
		labels = EngineTypeBitmask.to_labels(1)
		assert 'Бензиновый' in labels

	def test_diesel(self):
		"""Should detect DIESEL flag."""
		labels = EngineTypeBitmask.to_labels(2)
		assert 'Дизельный' in labels

	def test_electro(self):
		"""Should detect ELECTRO flag."""
		labels = EngineTypeBitmask.to_labels(4)
		assert 'Электрический' in labels

	def test_combined_petrol_turbo(self):
		"""Should detect combined PETROL + TURBO flags."""
		labels = EngineTypeBitmask.to_labels(33)  # 1 | 32
		assert 'Бензиновый' in labels
		assert 'Турбированный' in labels

	def test_empty_for_none(self):
		"""Should return empty list for None."""
		assert EngineTypeBitmask.to_labels(None) == []

	def test_empty_for_zero(self):
		"""Should return empty list for 0."""
		assert EngineTypeBitmask.to_labels(0) == []


class TestGRMTypeBitmaskMapping:
	"""Tests for GRMTypeBitmask mapping."""

	def test_belt(self):
		"""Should detect BELT flag."""
		labels = GRMTypeBitmask.to_labels(1)
		assert 'Ремень' in labels

	def test_chain(self):
		"""Should detect CHAIN flag."""
		labels = GRMTypeBitmask.to_labels(2)
		assert 'Цепь' in labels

	def test_combined(self):
		"""Should detect combined BELT + WET_BELT flags."""
		labels = GRMTypeBitmask.to_labels(65)  # 1 | 64
		assert 'Ремень' in labels
		assert 'Мокрый ремень' in labels

	def test_empty_for_none(self):
		"""Should return empty list for None."""
		assert GRMTypeBitmask.to_labels(None) == []


class TestPhaseRegulatorTypeMapping:
	"""Tests for PhaseRegulatorType mapping."""

	def test_input(self):
		"""Should return 'На впуске' for INPUT."""
		assert PhaseRegulatorType.to_label(1) == 'На впуске'

	def test_output(self):
		"""Should return 'На выпуске' for OUTPUT."""
		assert PhaseRegulatorType.to_label(2) == 'На выпуске'

	def test_dual(self):
		"""Should return 'На обоих валах' for DUAL."""
		assert PhaseRegulatorType.to_label(3) == 'На обоих валах'

	def test_complex(self):
		"""Should return 'Сложная' for COMPLEX."""
		assert PhaseRegulatorType.to_label(4) == 'Сложная'

	def test_none(self):
		"""Should return None for None."""
		assert PhaseRegulatorType.to_label(None) is None
