"""Tests for ``CountryRepository``.

Ключевое поведение SRP/root-cause: репозиторий строит запрос и возвращает
список объектов, не бросая ``HTTPException`` (HTTP-семантика — в эндпоинте).
"""

import asyncio
from typing import Any, Coroutine, TypeVar
from unittest.mock import AsyncMock, patch

from apps.geo.repositories.country import CountryRepository

T = TypeVar('T')


def _run(coro: Coroutine[Any, Any, T]) -> T:
	return asyncio.run(coro)


class TestCountryRepository:
	def test_list_all_returns_list(self):
		repo = CountryRepository()
		with patch.object(repo, '_fetch_all', new=AsyncMock(return_value=[])):
			result = _run(repo.list_all())
		assert result == []

	def test_list_all_selects_country(self):
		repo = CountryRepository()
		captured: dict[str, Any] = {}

		async def _capture(query: Any) -> list[Any]:
			captured['sql'] = str(query.compile(compile_kwargs={'literal_binds': True}))
			return []

		with patch.object(repo, '_fetch_all', new=_capture):
			_run(repo.list_all())

		assert 'country' in captured['sql'].lower()
