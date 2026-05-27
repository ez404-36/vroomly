from typing import Any, cast

from sqlalchemy import UUID
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship
from sqlalchemy.orm import backref as sa_backref

from common.models import ForeignKeyTo
from common.models.fields.foreign_key_to import PostgresOnDeleteFK
from common.models.scalars import LazyLoadArgumentType
from core.models import AutoSchemaBase


def get_foreign_key_mixin(  # noqa: PLR0913 — фасад для общего FK-миксина, число параметров обоснованно
	model: type[AutoSchemaBase],
	relation_name: str,
	back_populates: str | None,
	nullable: bool,
	verbose_name: str | None,
	lazy: LazyLoadArgumentType = 'select',
	on_delete: PostgresOnDeleteFK = 'CASCADE',
	back_uselist: bool = True,
):
	"""
	Миксин для связи модели с другой моделью через внешний ключ.
	Помимо внешнего ключа добавляет relationship.

	Параметр ``back_uselist=False`` нужен для 1:1-связей: на стороне
	родительской модели обратная коллекция будет скалярным атрибутом,
	а не InstrumentedList. По умолчанию ``True`` (обычная 1:N связь),
	что сохраняет обратную совместимость со всеми существующими
	вызовами.
	"""
	model_str = model.__name__
	mixin_name = f'{model_str}ForeignKeyMixin'
	field_name = f'{relation_name}_id'

	# TODO: в качестве ID может быть не только UUID
	annotations = {field_name: Mapped[UUID | None] if nullable else Mapped[UUID]}

	if nullable and on_delete is None:
		on_delete: PostgresOnDeleteFK = 'SET NULL'

	def make_column():
		return mapped_column(ForeignKeyTo(model, on_delete), doc=verbose_name, nullable=nullable)

	def make_backref(name: str | None):
		if name is None:
			return None
		if back_uselist:
			return name
		return sa_backref(name, uselist=False)

	attrs: dict[str, Any] = {
		'extend_existing': True,
		'__annotations__': annotations,
		field_name: declared_attr(lambda cls: make_column()),
		relation_name: declared_attr(
			lambda cls, _model_str=model_str, _field_name=field_name, _lazy=lazy, _back_pop=back_populates: (
				relationship(
					_model_str,
					foreign_keys=lambda: getattr(cls, _field_name),
					backref=make_backref(cast(str, _back_pop) if _back_pop else None),
					lazy=_lazy,
				)
			)
		),
	}

	return type(mixin_name, (), attrs)
