from pydantic import BaseModel


class LibreTranslateDetectedLanguage(BaseModel):
	"""Определенный переводчиком язык"""

	confidence: int
	language: str


class LibreTranslateResponse(BaseModel):
	"""Модель ответа LibreTranslate"""

	# camelCase-имена обязательны: их возвращает LibreTranslate API,
	# переименование сломает десериализацию pydantic.
	translatedText: str  # noqa: N815
	alternatives: list[str]
	detectedLanguage: LibreTranslateDetectedLanguage | None = None  # noqa: N815
