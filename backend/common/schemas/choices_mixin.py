from typing import Iterable

from common.schemas.fields import ID


class ChoicesMixin:
	"""Миксин для добавления метода choices"""

	__labels__: dict[ID, str] = NotImplemented

	@classmethod
	def choices(cls) -> Iterable[tuple[ID, str]]:
		return cls.__labels__.items()

	@classmethod
	def get_label(cls, value: ID) -> str:
		"""Получить label по значению"""
		return cls.__labels__.get(value, 'undefined')
