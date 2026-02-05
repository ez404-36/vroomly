import csv
import pickle
from pathlib import Path
from typing import Any, Collection, Iterable, TypeVar

from apps.vehicles.models.vehicle.vehicle_engine import VehicleEngine
from core.models import AutoSchemaBase

T = TypeVar('T', bound=type[AutoSchemaBase])


class PklToCsvImportBase[T]:
    """
    Преобразовывает данные из Pickle файлов в CSV файлы
    """

    model: T
    csv_fields: Collection[str]
    source_path: Path | str
    output_path: Path | str

    def run(self, pkl_file: Path | str):
        with open(pkl_file, 'rb') as f_obj:
            instances: list[T] = pickle.load(f_obj)

        with open(self.output_path, 'w', encoding='utf-8', newline='') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=self.csv_fields)

            csv_writer.writeheader()

            for instance in instances:
                transformed_data = self.transform(instance)
                csv_writer.writerow(transformed_data)

    async def prefetch_data(self) -> dict[str, dict[Any, Any]]:
        return {}

    def transform(self, model: T) -> dict:
        raise NotImplementedError


class PklToCsvEngineImport(PklToCsvImportBase[VehicleEngine]):
    model = VehicleEngine

    csv_fields = [
        'brand',
        'concern',
    ]
