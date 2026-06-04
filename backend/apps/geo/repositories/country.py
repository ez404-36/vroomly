"""Репозиторий доступа к данным ``Country``."""

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.geo.models.country import Country
from core.db import database


class CountryRepository:
	"""Доступ к данным стран. Методы возвращают список объектов или ``None``."""

	def __init__(self, session: AsyncSession | None = None) -> None:
		"""
		:param session: внешняя сессия. Если не передана, методы открывают
			собственную короткоживущую сессию через ``database``.
		"""
		self._session = session

	async def list_all(self) -> list[Country]:
		"""Вернуть все страны."""
		return await self._fetch_all(select(Country))

	async def _fetch_all(self, query: Select[tuple[Country]]) -> list[Country]:
		"""Выполнить ``select`` (множество) через внешнюю или собственную сессию."""
		if self._session is not None:
			return list(await database.session_fetch_all(self._session, query))
		return list(await database.fetch_all(query))
