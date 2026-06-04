"""Репозиторий доступа к данным ``User``."""

from uuid import UUID

from sqlalchemy import Select, and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.accounts.models.user import User
from core.db import database


class UserRepository:
	"""Доступ к данным пользователей. Методы поиска возвращают объект или ``None``."""

	def __init__(self, session: AsyncSession | None = None) -> None:
		"""
		:param session: внешняя сессия. Если не передана, методы открывают
			собственную короткоживущую сессию через ``database``.
		"""
		self._session = session

	async def get_by_id(self, user_id: UUID) -> User | None:
		"""Вернуть пользователя по первичному ключу или ``None``."""
		query = select(User).where(User.id == user_id)
		return await self._fetch_one(query)

	async def get_active_by_login_or_email(self, identifier: str) -> User | None:
		"""
		Вернуть не удалённого пользователя по совпадению login или email, иначе ``None``.

		Не бросает исключений — отсутствие пользователя выражается через ``None``.
		"""
		query = select(User).where(
			and_(
				or_(
					User.login == identifier,
					User.email == identifier,
				),
				User.deleted.isnot(True),
			)
		)
		return await self._fetch_one(query)

	async def _fetch_one(self, query: Select[tuple[User]]) -> User | None:
		"""Выполнить ``select`` через внешнюю или собственную сессию."""
		if self._session is not None:
			return await database.session_fetch_one(self._session, query)
		return await database.fetch_one(query)
