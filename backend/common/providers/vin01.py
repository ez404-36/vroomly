from common.providers.base_api_provider import BaseApiProvider


class Vin01ApiError(Exception):
	"""Ошибка взаимодействия с API vin-01.ru."""


class VinO1ApiProvider(BaseApiProvider):
	"""Клиент API vin-01.ru."""

	base_url = 'https://vin-01.ru'
