from common.providers.base_api_provider import BaseApiProvider
from common.providers.translators.base import AbstractTranslator
from core.settings import settings
from pydantic import BaseModel


class LibreTranslateDetectedLanguage(BaseModel):
    """Определенный переводчиком язык"""

    confidence: int
    language: str


class LibreTranslateResponse(BaseModel):
    """Модель ответа LibreTranslate"""

    translatedText: str
    alternatives: list[str]
    detectedLanguage: LibreTranslateDetectedLanguage | None = None


class LibreTranslate(AbstractTranslator, BaseApiProvider):
    """
    Клиент для использования libretranslate
    """

    base_url = settings.libretranslate.url

    def get_languages(self):
        """Список доступных языков"""
        return self.get("languages")

    def translate(
        self, text: str, source: str = "ru", target: str = "en", fmt: str = "text", **kwargs
    ) -> str:
        """
        Перевод текста.
        :param text: Переводимый текст
        :param source: С какого языка (Префикс языка или 'auto')
        :param target: На какой язык
        :param fmt: Формат данных
        """

        payload = {
            "q": text,
            "source": source,
            "target": target,
            "format": fmt,
            "alternatives": 3,
        }
        raw_response = self.post(
            "translate",
            payload=payload,
            headers={"Content-Type": "application/json"},
        )
        response: LibreTranslateResponse = LibreTranslateResponse(**raw_response)
        return response.translatedText
