from sqlalchemy import ForeignKey

from core.models.base import AutoSchemaBase


def ForeignKeyTo(model: type[AutoSchemaBase]):  # noqa
    ref = f'{model.__table_args__.get("schema", "public")}.{model.__tablename__}.id'
    return ForeignKey(ref)
