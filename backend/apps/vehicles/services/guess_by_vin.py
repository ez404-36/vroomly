"""Оркестрация подбора данных ТС по VIN для предзаполнения формы.

Сервис только координирует шаги: запрос к VIN-провайдеру → подбор бренда/модели/
поколений/комплектаций (``GuessCommonCarInfo``). Возвращает доменный результат
(сырые данные VIN-провайдера + подобранные из БД данные); сборку HTTP-ответа
делает ``api/car_info/mappers``.
"""

from dataclasses import dataclass

from apps.vehicles.integrations.car_info_by_vin.provider import CarInfoByVinProvider
from apps.vehicles.integrations.car_info_by_vin.schema import CarInfoByVinDataSchema
from apps.vehicles.services.guess_common_car_info import (
	GuessCommonCarInfo,
	GuessCommonCarInfoSchema,
)


@dataclass(frozen=True)
class GuessByVinResult:
	"""Доменный результат подбора данных ТС по VIN.

	Объединяет сырые данные VIN-провайдера (``car_info``) и подобранные из
	каталога бренд/модель/поколения/комплектации (``guess``).
	"""

	car_info: CarInfoByVinDataSchema
	guess: GuessCommonCarInfoSchema


class GuessByVinService:
	"""Оркестратор: VIN-провайдер → подбор данных ТС из каталога."""

	def __init__(self) -> None:
		self._provider = CarInfoByVinProvider()
		self._guess = GuessCommonCarInfo()

	async def guess(self, vin: str) -> GuessByVinResult:
		"""Подобрать данные ТС по VIN.

		:returns: ``GuessByVinResult`` с сырыми данными VIN-провайдера и
			подобранными из БД бренд/модель/поколениями/комплектациями.
		:raises GuessCommonCarInfoError: если бренд/модель определить не удалось.
		"""
		car_info = self._provider.get_info(vin)
		guess = await self._guess.get_from_vin01(car_info)
		return GuessByVinResult(car_info=car_info, guess=guess)
