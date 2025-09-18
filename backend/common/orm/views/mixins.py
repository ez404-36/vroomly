from apps.accounts.api.schemas.readers import UserDetail
from apps.accounts.api.utils import request_user


class AuthenticatedUserAPIMixin:
    """
    Миксин для API-классов, разрешающий использовать эндпоинты этого класса
    только авторизованным пользователям.
    """

    user: UserDetail = request_user
