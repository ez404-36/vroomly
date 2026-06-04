"""Оркестрация подбора основной информации об автомобиле по данным VIN-провайдера.

Сервис только координирует шаги: перевод названия → подбор бренда/модели/поколений/
комплектаций (через ``CarCatalogRepository``) → сборка схемы (через mappers).
Доступ к данным живёт в ``repositories/``, представление — в ``api/car_info/mappers``.
"""

from pydantic import BaseModel, Field

from apps.vehicles.api.car_info.mappers import trims_to_choices
from apps.vehicles.integrations.car_info_by_vin.schema import CarInfoByVinDataSchema
from apps.vehicles.models.vehicle.vehicle_brand import VehicleBrand
from apps.vehicles.repositories.car_catalog import CarCatalogRepository
from apps.vehicles.repositories.fuzzy_lookup import GuessCommonCarInfoError
from common.providers.translators.main import Translator
from common.schemas.choices_utils import to_choice_field, to_choice_field_list
from common.schemas.fields import ChoiceFieldSchema, TrimChoiceSchema

__all__ = (
	'GuessCommonCarInfo',
	'GuessCommonCarInfoError',
	'GuessCommonCarInfoSchema',
)


class GuessCommonCarInfoSchema(BaseModel):
	"""
	Данные об автомобиле, полученные в результате обработки
	информации по VIN-номеру, предоставленной внешним источником
	"""

	brand: ChoiceFieldSchema = Field(description='Бренд')
	model: ChoiceFieldSchema = Field(description='Модель')
	generations: list[ChoiceFieldSchema] = Field(description='Поколение')
	trims: list[TrimChoiceSchema] = Field(description='Комплектация')


class GuessCommonCarInfo:
	"""
	Сервис, отвечающий за предоставление основной информации об автомобиле
	по информации по VIN-номеру, предоставленной внешним источником
	"""

	def __init__(self) -> None:
		self._catalog = CarCatalogRepository()
		self._translator = Translator()

	async def get_from_vin01(self, data: CarInfoByVinDataSchema) -> GuessCommonCarInfoSchema:
		"""Подобрать бренд/модель/поколения/комплектации по данным VIN-провайдера."""
		brand_and_series_ru = data.model.split()

		guess_brand, brand_word_count = await self._resolve_brand(brand_and_series_ru)

		series_ru = ' '.join(brand_and_series_ru[brand_word_count:])
		series_en = self._translator.translate(series_ru)
		guess_series = await self._catalog.find_series(guess_brand.id, series_en)
		if guess_series is None:
			raise GuessCommonCarInfoError(
				f'Не удалось определить модель марки {guess_brand.name}: {series_ru} -> {series_en}'
			)

		guess_generations = await self._catalog.list_generations(guess_series.id, data.year)
		guess_trims = await self._catalog.list_trims([generation.id for generation in guess_generations])

		return GuessCommonCarInfoSchema(
			brand=to_choice_field(guess_brand),
			model=to_choice_field(guess_series),
			generations=to_choice_field_list(guess_generations),
			trims=trims_to_choices(guess_trims),
		)

	async def _resolve_brand(self, brand_and_series_ru: list[str]) -> tuple[VehicleBrand, int]:
		"""
		Определить бренд, расширяя префикс названия слово за словом.

		:returns: кортеж ``(бренд, число слов префикса)`` для отделения модели.
		:raises GuessCommonCarInfoError: если бренд определить не удалось.
		"""
		word_count = 0
		total_words = len(brand_and_series_ru)
		brand_ru: str | None = None
		brand_en: str | None = None

		while word_count < total_words:
			word_count += 1
			brand_ru = ' '.join(brand_and_series_ru[:word_count])
			brand_en = self._translator.translate(brand_ru)
			guess_brand = await self._catalog.find_brand(brand_en)
			if guess_brand is not None:
				return guess_brand, word_count

		raise GuessCommonCarInfoError(f'Не удалось определить марку: {brand_ru} -> {brand_en}')
