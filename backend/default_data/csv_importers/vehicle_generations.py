from apps.vehicles.models.vehicle.vehicle_generation import VehicleGeneration
from default_data.csv_importers.base import ImportObjectsFromCSVBase

_TRUE_VALUES = frozenset({'t', 'true', '1', 'yes', 'y'})
_FALSE_VALUES = frozenset({'f', 'false', '0', 'no', 'n'})


class ImportVehicleGenerationsCSV(ImportObjectsFromCSVBase):
    """
    Импорт поколений ТС.

    Помимо стандартного приведения числовых полей, преобразует строковое
    представление булевого ``is_restyling`` в Python-bool: базовый импортёр
    не умеет работать с булевыми колонками.
    """

    model = VehicleGeneration
    source_filename = 'vehicle_generation.csv'

    def transform_object_data(self, instance_data: dict) -> dict:
        instance_data = super().transform_object_data(instance_data)

        raw = instance_data.get('is_restyling')
        if isinstance(raw, str):
            normalized = raw.strip().lower()
            if normalized in _TRUE_VALUES:
                instance_data['is_restyling'] = True
            elif normalized in _FALSE_VALUES:
                instance_data['is_restyling'] = False

        return instance_data
