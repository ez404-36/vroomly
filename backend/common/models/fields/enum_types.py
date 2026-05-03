__all__ = (
    'IntFlagType',
    'IntEnumType',
    'IntEnumArrayType'
)

import enum

from sqlalchemy import ARRAY
from sqlalchemy.types import SmallInteger, TypeDecorator


class IntFlagType(TypeDecorator):
    """
    Используется для сохранения в БД числовых значений IntFlag.
    Позволяет использовать битовые операции.
    """

    impl = SmallInteger
    cache_ok = True

    def __init__(self, enum_class: type[enum.Flag | enum.IntFlag], *args, **kwargs):
        self.enum_class = enum_class
        super().__init__(*args, **kwargs)

    def process_bind_param(self, value, _dialect):
        # При сохранении в БД: из IntFlag в int
        if value is None:
            return None
        if isinstance(value, self.enum_class):
            return value.value
        elif isinstance(value, str) and value.isdigit():
            return int(value)
        elif isinstance(value, int):
            return value
        raise ValueError(f'Expected {self.enum_class}, got {type(value)}')

    def process_result_value(self, value, _dialect):
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

    def __init__(self, enum_class: type[enum.Enum | enum.IntEnum], *args, **kwargs):
        self.enum_class = enum_class
        super().__init__(*args, **kwargs)

    def process_bind_param(self, value, _dialect) -> int | None:
        if value is None:
            return None
        if isinstance(value, str):
            return int(value)
        if isinstance(value, int):
            return value
        return value.value

    def process_result_value(self, value, _dialect):
        return self.enum_class(value) if value is not None else None


class IntEnumArrayType(TypeDecorator):
    """
    Используется для сохранения в БД списка числовых значений Enum.
    (Иначе Postgres по умолчанию создаёт свой строковый тип Enum).
    Минус по сравнению с нативным PgEnum - нет ограничения значений на уровне БД
    """

    impl = ARRAY(SmallInteger)
    cache_ok = True

    def __init__(self, enum_class: type[enum.Enum], *args, **kwargs):
        self.enum_class = enum_class
        super().__init__(*args, **kwargs)

    def process_bind_param(self, value, _dialect):
        if value is None:
            return None

        return [
            item.value if isinstance(item, self.enum_class) else item
            for item in value
        ]

    def process_result_value(self, value, _dialect):
        if value is None:
            return None
        return [self.enum_class(item) for item in value]
