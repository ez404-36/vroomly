import csv
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from core.models.base import AutoSchemaBase


class ImportFromCSVBase:
    """
    Базовый класс импорта данных из CSV-файла в БД
    """

    model: type[AutoSchemaBase]

    """
    Маппер столбцов csv на поля в модели.
    Если названия совпадают, можно не указывать.
    Если данные будут браться из prefetch_data(), то значение записывается в виде:
    $instance_name:$fk_field.
    Пример: 
    prefetched_data = {'brands': {'GAC': 15, 'BMW': 35}}
    mapper = {
        'brand': 'brands:brand_id',
        # поле в csv: 'ключ в prefetched_data:внешний ключ для связи с маркой ТС'
    }
    """
    mapper: dict[str, str] = {}

    filename: str = NotImplemented
    default_data = {}   # данные по умолчанию для создаваемых сущностей

    def __init__(self, session: Session | AsyncSession) -> None:
        self.session = session

    async def run(self):
        prefetched_data = await self.prefetch_data()

        with open(Path(__file__).parent.parent / 'csv_files' / self.filename) as f_obj:
            reader = csv.DictReader(f_obj)

            instances = []
            for row in reader:
                instance_data = {}
                for key, value in row.items():
                    if key is None or key.startswith('_'):
                        # столбцы, которые начинаются с _, будут игнорироваться
                        continue

                    mapped_key = self.mapper.get(key, key)
                    if ':' in mapped_key:
                        prefetched_data_field, fk_field = mapped_key.split(':')
                        if prefetched_data_field not in prefetched_data:
                            raise ValueError(f'Вспомогательные данные по {prefetched_data_field} не были загружены из БД')

                        related_instances = prefetched_data[prefetched_data_field]
                        instance_data[fk_field] = related_instances[value]
                    else:
                        instance_data[mapped_key] = value

                instance_data.update(**self.default_data)
                instance = self.model(**instance_data)
                instances.append(instance)

        self.session.add_all(instances)

    async def prefetch_data(self) -> dict[str, dict[Any, Any]]:
        """
        Загруженные из БД данные для маппинга данных из CSV-файла.
        Пример:
        1) Загрузка стран
        {'country': {$column_in_csv: $foreign_key_column}}
        country - обозначение типа сущности
        $column_in_csv - название столбца с данными о стране в CSV-файле
        $foreign_key_column - поле внешнего ключа для связи со страной в модели
        """
        return {}
