from sqlalchemy import String, event
from sqlalchemy.orm import Mapped, mapped_column

from common.utils.generators import generate_code
from core.models import AutoSchemaBase


class CodeModelMixin:
	code: Mapped[str] = mapped_column(String(50), doc='КОД (англ. язык, верхний регистр)')


def __generate_code_listener(mapper, connection, target):
	"""Генерация кода марки ТС по аббревиатуре или названию марки"""
	if not target.code:
		target.code = generate_code(getattr(target, 'abbreviation', None) or getattr(target, 'name', None) or '')


def generate_code_on_create(model: type[AutoSchemaBase]):
	"""Регистрирует SQLAlchemy listener, заполняющий поле ``code`` перед вставкой."""
	event.listens_for(model, 'before_insert')(__generate_code_listener)
