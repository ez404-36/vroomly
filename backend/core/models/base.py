import re
import uuid
from collections import defaultdict

from pydantic.v1 import UUID4
from sqlalchemy import Column, UUID
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

Base = declarative_base()


class AutoSchemaBase(Base):
    __abstract__ = True

    id: Mapped[UUID4] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()

        if cls.__name__.endswith('Abstract'):
            return

        module_name = cls.__module__
        schema_name = module_name.split(".")[1]

        # Задаём название таблицы
        cls.__tablename__ = cls.get_table_name()

        # Если __table_args__ ещё не задан или не словарь — задаём
        table_args = getattr(cls, "__table_args__", None)

        if table_args is None:
            cls.__table_args__ = {"schema": schema_name}
        elif isinstance(table_args, dict):
            # обновляем, не перезаписываем
            table_args.setdefault("schema", schema_name)
            cls.__table_args__ = table_args
        elif isinstance(table_args, tuple):
            # если __table_args__ — кортеж с доп. опциями и словарём, обновим словарь
            *args, last = table_args
            if isinstance(last, dict):
                last.setdefault("schema", schema_name)
                cls.__table_args__ = (*args, last)
            else:
                # если словаря нет, добавим новый
                cls.__table_args__ = (*table_args, {"schema": schema_name})

    @classmethod
    def get_table_name(cls) -> str:
        """
        Преобразует имя класса в имя таблицы в БД (если не задано внутри класса) по принципу:
        CamelCase в snake_case
        """

        if existing_table_name := getattr(cls, "__tablename__", None):
            return existing_table_name

        pattern = r"(?<!^)(?=[A-Z])"

        return re.sub(pattern, "_", cls.__name__).lower()

    def validate(self) -> dict[str, list]:
        """
        Валидирует модель и возвращает список ошибок по полю
        """
        errors = defaultdict(list)
        required_error = 'Обязательное поле'

        for col in self.get_table_columns():
            col_name = col.name

            if col_name == 'id':
                continue

            col_value = getattr(self, col_name)
            if col_value is None and col.nullable is False:
                errors[col_name].append(required_error)

        return dict(errors)

    def get_table_columns(self) -> list[Column]:
        return list(self.__table__.columns)
