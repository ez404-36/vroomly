from pydantic.v1 import UUID4
from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr

from common.models import ForeignKeyTo
from common.models.scalars import LazyLoadArgumentType
from core.models import AutoSchemaBase


def get_foreign_key_mixin(
    model: type[AutoSchemaBase],
    relation_name: str,
    back_populates: str | None,
    nullable: bool,
    verbose_name: str | None,
    lazy: LazyLoadArgumentType = "select",
):
    """
    Миксин для связи модели с другой моделью через внешний ключ.
    Помимо внешнего ключа добавляет relationship.
    """
    model_str = model.__name__
    mixin_name = f'{model_str}ForeignKeyMixin'
    field_name = f'{relation_name}_id'

    annotations = {
        field_name: Mapped[UUID4 | None] if nullable else Mapped[UUID4]
    }

    attrs = {
        "__annotations__": annotations,
        field_name: declared_attr(
            lambda cls, _model=model, _doc=verbose_name, _nullable=nullable: mapped_column(
                ForeignKeyTo(_model), doc=_doc, nullable=_nullable
            )
        ),
        relation_name: declared_attr(
            lambda cls, _model_str=model_str, _field_name=field_name, _lazy=lazy, _back_pop=back_populates: relationship(
                _model_str,
                foreign_keys=lambda: getattr(cls, _field_name),
                back_populates=_back_pop,
                lazy=_lazy,
            )
        ),
    }

    return type(mixin_name, (), attrs)
