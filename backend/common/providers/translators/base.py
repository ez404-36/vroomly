from abc import ABC, abstractmethod


class AbstractTranslator(ABC):
	"""
	Абстрактный класс языкового переводчика
	"""

	@abstractmethod
	def translate(self, text: str, source: str = "ru", target: str = "en", **kwargs) -> str:
		"""
		Перевод текста
		:param text: Исходный текст
        :param source: С какого языка (Префикс языка или 'auto')
        :param target: На какой язык
		"""
		raise NotImplementedError
