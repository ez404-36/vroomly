"""Tests for GuessByVinService — оркестрация подбора данных ТС по VIN.

Сервис только координирует шаги: VIN-провайдер → ``GuessCommonCarInfo``.
Провайдер и сервис подбора мокаются; внешних обращений нет.
"""

import asyncio
from typing import Any, Coroutine, TypeVar
from unittest.mock import AsyncMock, MagicMock, patch

from apps.vehicles.services.guess_by_vin import GuessByVinResult, GuessByVinService

T = TypeVar('T')

_PROVIDER = 'apps.vehicles.services.guess_by_vin.CarInfoByVinProvider'
_GUESS = 'apps.vehicles.services.guess_by_vin.GuessCommonCarInfo'


def _run(coro: Coroutine[Any, Any, T]) -> T:
	return asyncio.run(coro)


class TestGuessByVinService:
	def test_orchestrates_provider_then_guess(self) -> None:
		"""VIN передаётся провайдеру, car_info — в подбор; результат объединяет оба."""
		car_info = MagicMock()
		guess = MagicMock()

		provider = MagicMock()
		provider.get_info = MagicMock(return_value=car_info)
		guess_service = MagicMock()
		guess_service.get_from_vin01 = AsyncMock(return_value=guess)

		with (
			patch(_PROVIDER, return_value=provider),
			patch(_GUESS, return_value=guess_service),
		):
			result = _run(GuessByVinService().guess('1HGCM82633A004352'))

		assert isinstance(result, GuessByVinResult)
		assert result.car_info is car_info
		assert result.guess is guess
		provider.get_info.assert_called_once_with('1HGCM82633A004352')
		guess_service.get_from_vin01.assert_awaited_once_with(car_info)
