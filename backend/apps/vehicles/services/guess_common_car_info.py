from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy import and_, between, select

from apps.vehicles.integrations.car_info_by_vin.schema import CarInfoByVinDataSchema
from apps.vehicles.models.car.car_trim import CarTrim
from apps.vehicles.models.vehicle.vehicle_brand import VehicleBrand
from apps.vehicles.models.vehicle.vehicle_generation import VehicleGeneration
from apps.vehicles.models.vehicle.vehicle_series import VehicleSeries
from common.providers.translators.main import Translator
from common.schemas.choices_utils import to_choice_field, to_choice_field_list, to_choice_field_with_parent_list
from common.schemas.fields import ChoiceFieldSchema, ChoiceFieldWithParentSchema
from core.db import database


class GuessCommonCarInfoError(Exception): ...


class GuessCommonCarInfoSchema(BaseModel):
	"""
	Данные об автомобиле, полученные в результате обработки
	информации по VIN-номеру, предоставленной внешним источником
	"""

	brand: ChoiceFieldSchema = Field(description='Бренд')
	model: ChoiceFieldSchema = Field(description='Модель')
	generation: list[ChoiceFieldSchema] = Field(description='Поколение')
	configuration: list[ChoiceFieldWithParentSchema] = Field(description='Комплектация')


class GuessCommonCarInfo:
	"""
	Сервис, отвечающий за предоставление основной информации об автомобиле
	по информации по VIN-номеру, предоставленной внешним источником
	"""

	async def get_from_vin01(self, data: CarInfoByVinDataSchema) -> GuessCommonCarInfoSchema:
		translator = Translator()

		brand_and_series_ru = data.model.split()
		brand_ru = ' '.join(brand_and_series_ru[:-1])
		series_ru = ' '.join(brand_and_series_ru[-1])

		brand_en = translator.translate(brand_ru)
		series_en = translator.translate(series_ru)

		guess_brand = await self._guess_brand(brand_en)

		if not guess_brand:
			raise GuessCommonCarInfoError(f'Не удалось определить марку: {brand_ru} -> {brand_en}')

		guess_series = await self._guess_series(guess_brand.id, series_en)
		if not guess_series:
			raise GuessCommonCarInfoError(f'Не удалось определить модель марки {brand_en}: {series_ru} -> {series_en}')

		guess_generations = await self._guess_generations(guess_series.id, data.year)
		guess_trims = await self._guess_trims([it.id for it in guess_generations])

		return GuessCommonCarInfoSchema(
			brand=to_choice_field(guess_brand),
			model=to_choice_field(guess_series),
			generation=to_choice_field_list(guess_generations),
			configuration=to_choice_field_with_parent_list(guess_trims, ''),
		)

	@staticmethod
	async def _guess_brand(brand_en: str) -> VehicleBrand | None:
		guess_brand_query = select(VehicleBrand).where(VehicleBrand.name == brand_en)

		return await database.fetch_one(guess_brand_query)

	@staticmethod
	async def _guess_series(brand_id: UUID, model_en: str) -> VehicleSeries | None:
		guess_series_query = select(VehicleSeries).where(
			and_(
				VehicleSeries.brand_id == brand_id,
				VehicleSeries.name == model_en,
			)
		)

		return await database.fetch_one(guess_series_query)

	@staticmethod
	async def _guess_generations(model_id: UUID, car_production_year: int) -> list[VehicleGeneration]:
		guess_generation_query = select(VehicleGeneration).where(
			and_(
				VehicleGeneration.model_id == model_id,
				between(car_production_year, VehicleGeneration.start_year, VehicleGeneration.end_year),
			)
		)

		return await database.fetch_all(guess_generation_query)

	@staticmethod
	async def _guess_trims(generation_ids: list[UUID], **kwargs: None) -> list[CarTrim]:
		if not generation_ids:
			return []

		trim_query = select(CarTrim).where(CarTrim.generation_id.in_(generation_ids))

		return await database.fetch_all(trim_query)
