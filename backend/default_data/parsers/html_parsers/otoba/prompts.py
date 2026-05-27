"""
Промпты для LLM, разбирающего страницы otoba.ru.

Текст шаблонов вынесен в ``prompt_template.txt`` (HTML-примеры с обильным
trailing-whitespace плохо ладят с линтером в исходниках). Шаблон читается
один раз при импорте модуля.
"""

from pathlib import Path

_TEMPLATE_PATH = Path(__file__).with_name('prompt_template.txt')
_VEHICLE_GENERATION_TEMPLATE = _TEMPLATE_PATH.read_text(encoding='utf-8')


def parse_vehicle_generation_prompt(html: str) -> str:
	"""Возвращает готовый prompt для LLM по странице поколения автомобиля."""
	# Дополнительный отступ "\n    " ровно повторяет исходный triple-quoted
	# layout, на который LLM-промпт исторически калиброван.
	return _VEHICLE_GENERATION_TEMPLATE + '\n    ' + html + '\nОтвет:\n'
