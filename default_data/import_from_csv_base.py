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
    mapper: dict[str, str] = NotImplemented     # {ключ в csv: поле в модели} (если отличаются)
    filename: str = NotImplemented

    def __init__(self, session: Session | AsyncSession) -> None:
        self.session = session

    async def run(self):
        prefetched_data = await self.prefetch_data()

        with open(Path(__file__).parent / 'csv_files' / self.filename) as f_obj:
            reader = csv.DictReader(f_obj)

            instances = []
            for row in reader:
                instance_data = {}
                for key, value in row.items():
                    if key is None:
                        continue

                    mapped_key = self.mapper.get(key, key)
                    if ':' in mapped_key:
                        mapped_key, instance_column = mapped_key.split(':')
                        instance_name, _ = instance_column.rsplit('.')
                        if instance_name not in prefetched_data:
                            raise ValueError(f'Вспомогательные данные по {instance_name} не были загружены из БД')

                        instance_data[mapped_key] = prefetched_data[instance_name][value]
                    else:
                        instance_data[mapped_key] = value
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
