"""Бизнес-логика управления профилем пользователя."""

from uuid import UUID

from apps.accounts.models.user import User
from apps.accounts.repositories.user import UserRepository
from common.schemas.models import UpdateUserProfile
from core.db import database


class ProfileService:
	"""Обновление профиля пользователя."""

	async def update(self, user_id: UUID, data: UpdateUserProfile) -> User | None:
		"""
		Частично обновить профиль пользователя (только переданные поля).

		:returns: обновлённый ``User``; ``None``, если пользователь не найден.
		"""
		async with database.get_async_session() as session:
			user = await UserRepository(session).get_by_id(user_id)
			if user is None:
				return None

			update_data = data.model_dump(exclude_unset=True)
			for field, value in update_data.items():
				setattr(user, field, value)

			await session.commit()
			await session.refresh(user)
			return user
