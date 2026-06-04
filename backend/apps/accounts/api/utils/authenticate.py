"""Тонкая обёртка над аутентификацией.

Делегирует в ``AuthService.authenticate``. Возвращает ``User | None`` единообразно
(не бросает ``HTTPException`` и не различает «не найден» / «неверный пароль»);
HTTP-семантика — ответственность слоя эндпоинтов.
"""

__all__ = ('authenticate_user',)

from apps.accounts.models.user import User
from apps.accounts.services.auth import AuthService


async def authenticate_user(username: str, password: str) -> User | None:
	"""Аутентифицировать пользователя по login или email + паролю."""
	return await AuthService().authenticate(username, password)
