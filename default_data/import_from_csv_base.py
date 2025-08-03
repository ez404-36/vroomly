import csv
from pathlib import Path

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
    def run(cls, session: Session | AsyncSession):
        with open(Path(__file__).parent / 'csv_files' / cls.filename) as f_obj:
            reader = csv.DictReader(f_obj)

            instances = [
                cls.model(**{
                    cls.mapper[k]: v for k, v in row.items()
                })
                for row in reader
            ]

        session.add_all(instances)
