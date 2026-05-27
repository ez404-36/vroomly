from common.depends import request_user
from common.schemas.models import CurrentUser


class AuthenticatedUserAPIMixin:
	"""
	Миксин для API-классов, разрешающий использовать эндпоинты этого класса
	только авторизованным пользователям.
	"""

	user: CurrentUser = request_user


class BaseAPI(
	AuthenticatedUserAPIMixin,
):
	"""
	Базовый класс для всех API, которыми может пользоваться авторизованный пользователь
	"""
