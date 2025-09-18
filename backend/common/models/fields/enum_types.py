__all__ = (
    "IntFlagType",
    "IntEnumType",
)

import enum

from sqlalchemy.types import SmallInteger, TypeDecorator


class IntFlagType(TypeDecorator):
    """
    Используется для сохранения в БД числовых значений IntFlag.
    Позволяет использовать битовые операции.
    """

    impl = SmallInteger
    cache_ok = True

    def __init__(self, enum_class: enum.Flag | enum.IntFlag, *args, **kwargs):
        self.enum_class = enum_class
        super().__init__(*args, **kwargs)

    def process_bind_param(self, value, dialect):
        # При сохранении в БД: из IntFlag в int
        if value is None:
            return None
        if isinstance(value, self.enum_class):
            return value.value
        raise ValueError(f"Expected {self.enum_class}, got {type(value)}")

    def process_result_value(self, value, dialect):
        # При чтении из БД: из int в IntFlag
        if value is None:
            return None
        return self.enum_class(value)


class IntEnumType(TypeDecorator):
    """
    Используется для сохранения в БД числовых значений Enum
    (Иначе Postgres по умолчанию создаёт свой строковый тип Enum).
    Минус по сравнению с нативным PgEnum - нет ограничения значений на уровне БД
    """

    impl = SmallInteger
    cache_ok = True

    def __init__(self, enum_class: enum.Flag | enum.IntFlag, *args, **kwargs):
        self.enum_class = enum_class
        super().__init__(*args, **kwargs)

    def process_bind_param(self, value, dialect):
        return value.value if value is not None else None

    def process_result_value(self, value, dialect):
        return self.enum_class(value) if value is not None else None
