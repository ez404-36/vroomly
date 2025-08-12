from sqlalchemy import ForeignKey

from core.models.base import AutoSchemaBase


def ForeignKeyTo(model: type[AutoSchemaBase]):  # noqa
    table_args = model.__table_args__
    if isinstance(table_args, tuple):
        table_args = [it for it in table_args if isinstance(it, dict)][0]

    schema = table_args.get('schema', 'public')
    ref = f'{schema}.{model.__tablename__}.id'
    return ForeignKey(ref)
