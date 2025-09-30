from typing import TYPE_CHECKING

from common.utils.utils import import_class
from core.settings import settings

if TYPE_CHECKING:
	from common.providers.translators.base import AbstractTranslator

Translator: type['AbstractTranslator'] = import_class(settings.translator_model)
