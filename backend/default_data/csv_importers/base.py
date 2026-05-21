import csv
from pathlib import Path
from typing import Any, Iterable, TypeVar

from sqlalchemy import DECIMAL, BigInteger, Float, Integer, Numeric, SmallInteger, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from common.models import IntEnumType, IntFlagType
from common.utils.generators import generate_code
from core.db import database
from core.models import AutoSchemaBase

T = TypeVar('T', bound=type[AutoSchemaBase])


def get_numeric_columns(model_class: type[AutoSchemaBase]) -> list[str]:
    """Возвращает список имен колонок, которые являются числовыми"""
    numeric_types = (
        Integer, BigInteger, SmallInteger,
        Float, Numeric, DECIMAL, IntEnumType, IntFlagType,
    )

    numeric_columns = []

    for column in model_class.get_table_columns():
        if isinstance(column.type, numeric_types):
            numeric_columns.append(column.name)

    return numeric_columns


class ImportObjectsFromCSVBase:
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

    source_filename: str = NotImplemented
    default_data = {}  # данные по умолчанию для создаваемых сущностей

    def __init__(self, session: Session | AsyncSession) -> None:
        self.session = session
        self.nullable_fields = None

        table_columns = self.model.get_table_columns()

        self.nullable_columns = set([col.name for col in table_columns if col.nullable])
        self.numeric_columns = set(get_numeric_columns(self.model))

        self.prefetched_data: dict[str, dict[Any, Any]] = {}


    async def run(self):
        await self.prefetch_data()

        with open(Path(__file__).parent.parent / 'csv_files' / self.source_filename) as f_obj:
            reader = csv.DictReader(f_obj)

            instances = []
            for row in reader:
                instance_data = {}
                for key, value in row.items():
                    if key is None or key.startswith('_'):
                        # столбцы, которые начинаются с _, будут игнорироваться
                        continue

                    mapped_key = self.mapper.get(key, key)

                    if value == '' and mapped_key in self.nullable_columns:
                        value = None
                    elif value and mapped_key in self.numeric_columns:
                        value = int(value)

                    instance_data[mapped_key] = value

                instance_data.update(**self.default_data)
                instance_data = self.transform_object_data(instance_data)
                instances.append(instance_data)

        await self.bulk_insert(instances)
        print(f'Обработано {len(instances)} записей {self.model}')

    async def bulk_insert(self, instances: list[dict], batch_size: int = 500):
        for i in range(0, len(instances), batch_size):
            batch = instances[i:i + batch_size]
            query = insert(self.model).values(batch)
            await self.session.execute(query)

    def transform_object_data(self, instance_data: dict) -> dict:
        """
        Преобразование входных данных создаваемого объекта
        """
        return instance_data

    async def prefetch_data(self):
        """
        Загруженные из БД данные для маппинга данных из CSV-файла.
        Пример:
        1) Загрузка стран
        {'country': {$column_in_csv: $foreign_key_column}}
        country - обозначение типа сущности
        $column_in_csv - название столбца с данными о стране в CSV-файле
        $foreign_key_column - поле внешнего ключа для связи со страной в модели
        """
        self.prefetched_data = {}

    async def prefetch_objects(self, model: T) -> Iterable[T]:
        return await database.session_fetch_all(
            self.session, select(model)
        )


class ImportObjectsFromCsvWithGenerateCode(ImportObjectsFromCSVBase):
    """
    Класс для объектов, содержащих поле code (наследующихся от CodeModelMixin)
    """

    """
    Из какого поля модели генерировать код.
    Будет выбрано первое не пустое значение
    """
    code_from_fields: Iterable[str] = ()

    def transform_object_data(self, instance_data: dict) -> dict:
        instance_data = super().transform_object_data(instance_data)

        if not instance_data.get('code'):
            for field in self.code_from_fields:
                if value := instance_data.get(field):
                    instance_data['code'] = generate_code(value)
                    break

        return instance_data
