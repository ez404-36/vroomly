from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy import select, and_, between

from apps.vehicles.integrations.car_info_by_vin.schema import CarInfoByVinDataSchema
from apps.vehicles.models.car.car_trim import CarTrim
from apps.vehicles.models.vehicle.vehicle_brand import VehicleBrand
from apps.vehicles.models.vehicle.vehicle_generation import VehicleGeneration
from apps.vehicles.models.vehicle.vehicle_series import VehicleSeries
from common.providers.translators.main import Translator
from common.schemas.choices_utils import to_choice_field, to_choice_field_list, to_choice_field_with_parent_list
from common.schemas.fields import ChoiceFieldSchema, ChoiceFieldWithParentSchema
from core.db import database


class GuessCommonCarInfoException(Exception): ...


class GuessCommonCarInfoSchema(BaseModel):
	brand: ChoiceFieldSchema = Field(description="Бренд")
	model: ChoiceFieldSchema = Field(description="Модель")
	generation: list[ChoiceFieldSchema] = Field(description="Поколение")
	configuration: list[ChoiceFieldWithParentSchema] = Field(description="Комплектация")


class GuessCommonCarInfo:
	"""
	Сервис, отвечающий за предоставление основной информации об автомобиле
	по некоторым входным параметрам
	"""
	async def get_from_vin01(self, data: CarInfoByVinDataSchema) -> GuessCommonCarInfoSchema:
		translator = Translator()

		brand_and_model_ru = data.model.split()
		brand_ru = " ".join(brand_and_model_ru[:-1])
		model_ru = " ".join(brand_and_model_ru[-1])

		brand_en = translator.translate(brand_ru)
		model_en = translator.translate(model_ru)

		guess_brand = await self._guess_brand(brand_en)

		if not guess_brand:
			raise GuessCommonCarInfoException(f'Не удалось определить марку: {brand_ru} -> {brand_en}')

		guess_model = await self._guess_brand_model(guess_brand.id, model_en)
		if not guess_model:
			raise GuessCommonCarInfoException(
				f'Не удалось определить модель марки {brand_en}: {model_ru} -> {model_en}'
			)

		guess_generation = await self._guess_generation(guess_model.id, data.year)
		guess_configuration = []    # TODO await self._guess_configuration()

		return GuessCommonCarInfoSchema(
			brand=to_choice_field(guess_brand),
			model=to_choice_field(guess_model),
			generation=to_choice_field_list(guess_generation),
			configuration=to_choice_field_with_parent_list(guess_configuration),
		)

	@staticmethod
	async def _guess_brand(brand_en: str) -> VehicleBrand | None:
		guess_brand_query = (
			select(VehicleBrand)
			.where(VehicleBrand.name == brand_en)
		)

		return await database.fetch_one(guess_brand_query)

	@staticmethod
	async def _guess_brand_model(brand_id: UUID, model_en: str) -> VehicleSeries | None:
		guess_model_query = (
			select(VehicleSeries)
			.where(
				and_(
					VehicleSeries.brand_id == brand_id,
					VehicleSeries.name == model_en,
				)
			)
		)

		return await database.fetch_one(guess_model_query)

	@staticmethod
	async def _guess_generation(model_id: UUID, car_production_year: int) -> list[VehicleGeneration]:
		guess_generation_query = (
			select(VehicleGeneration)
			.where(
				and_(
					VehicleGeneration.model_id == model_id,
					between(car_production_year, VehicleGeneration.start_year, VehicleGeneration.end_year),
				)
			)
		)

		return await database.fetch_all(guess_generation_query)

	@staticmethod
	async def _guess_configuration(generation_ids: list[UUID], **kwargs) -> list[CarTrim]:
		# TODO
		print(generation_ids)
		return []
