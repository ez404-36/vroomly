import csv
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from core.models.base import AutoSchemaBase


class ImportFromCSVBase:
    """
    Базовый класс импорта данных из CSV-файла в БД
    """

    model: type[AutoSchemaBase]
    mapper: dict[str, str] = NotImplemented     # {ключ в csv: поле в модели}
    filename: str = NotImplemented

    @classmethod
    async def run(cls, session: Session | AsyncSession):
        prefetched_data = await cls.prefetch_data(session)

        with open(Path(__file__).parent / 'csv_files' / cls.filename) as f_obj:
            reader = csv.DictReader(f_obj)

            instances = []
            for row in reader:
                instance_data = {}
                for key, value in row.items():
                    if key is None:
                        continue

                    mapped_key = cls.mapper.get(key, key)
                    if ':' in mapped_key:
                        mapped_key, instance_column = mapped_key.split(':')
                        instance_name, _ = instance_column.rsplit('.')
                        if instance_name not in prefetched_data:
                            raise ValueError(f'Вспомогательные данные по {instance_name} не были предзагружены')

                        instance_data[mapped_key] = prefetched_data[instance_name][value]
                    else:
                        instance_data[mapped_key] = value
                instance = cls.model(**instance_data)
                instances.append(instance)

        session.add_all(instances)

    @classmethod
    async def prefetch_data(cls, session: Session | AsyncSession) -> dict[str, dict[Any, AutoSchemaBase]]:
        return {}
