"""Базовый репозиторий: общий доступ к данным без знания про HTTP."""

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import database
from core.models import AutoSchemaBase

TModel = TypeVar('TModel', bound=AutoSchemaBase)


class BaseRepository(Generic[TModel]):
	"""
	Базовый класс репозитория для модели ``AutoSchemaBase``.

	Инкапсулирует построение запросов и работу с сессией. Методы поиска
	возвращают ORM-объект или ``None`` — преобразование ``None`` → HTTP-ошибку
	(404) остаётся ответственностью слоя эндпоинтов, репозиторий про HTTP не знает.
	"""

	model: type[TModel]

	def __init__(self, session: AsyncSession | None = None) -> None:
		"""
		:param session: внешняя сессия. Если не передана, методы открывают
			собственную короткоживущую сессию через ``database``.
		"""
		self._session = session

	async def get_by_id(self, entity_id: UUID) -> TModel | None:
		"""Вернуть запись по первичному ключу или ``None``."""
		query = select(self.model).where(self.model.id == entity_id)
		return await self._fetch_one(query)

	async def _fetch_one(self, query: Select[tuple[TModel]]) -> TModel | None:
		"""Выполнить ``select`` через внешнюю или собственную сессию."""
		if self._session is not None:
			return await database.session_fetch_one(self._session, query)
		return await database.fetch_one(query)

	async def _fetch_all(self, query: Select[tuple[TModel]]) -> list[TModel]:
		"""Выполнить ``select`` (множество) через внешнюю или собственную сессию."""
		if self._session is not None:
			return list(await database.session_fetch_all(self._session, query))
		return list(await database.fetch_all(query))
