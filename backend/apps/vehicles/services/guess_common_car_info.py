from typing import TypeVar, cast
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy import ColumnElement, and_, between, func, select
from sqlalchemy.orm import InstrumentedAttribute, selectinload

from apps.vehicles.integrations.car_info_by_vin.schema import CarInfoByVinDataSchema
from apps.vehicles.models.car.car_trim import CarTrim
from apps.vehicles.models.vehicle.vehicle_brand import VehicleBrand
from apps.vehicles.models.vehicle.vehicle_generation import VehicleGeneration
from apps.vehicles.models.vehicle.vehicle_series import VehicleSeries
from common.providers.translators.main import Translator
from common.schemas.choices_utils import to_choice_field, to_choice_field_list, to_choice_field_with_parent_list
from common.schemas.fields import ChoiceFieldSchema, ChoiceFieldWithParentSchema
from core.db import database
from core.models import AutoSchemaBase

TRIGRAM_THRESHOLD: float = 0.3
TRIGRAM_AMBIGUITY_EPS: float = 0.05
MIN_FUZZY_QUERY_LENGTH: int = 3

TFuzzyModel = TypeVar('TFuzzyModel', bound=AutoSchemaBase)


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

		brand_i_end = 0
		end_i = len(brand_and_series_ru)
		guess_brand: VehicleBrand | None = None
		brand_ru: str | None = None
		brand_en: str | None = None

		while not guess_brand and brand_i_end < end_i:
			brand_i_end += 1
			brand_ru = ' '.join(brand_and_series_ru[:brand_i_end])
			brand_en = translator.translate(brand_ru)
			guess_brand = await self._guess_brand(brand_en)

		if not guess_brand:
			raise GuessCommonCarInfoError(f'Не удалось определить марку: {brand_ru} -> {brand_en}')

		series_ru = ' '.join(brand_and_series_ru[brand_i_end:])
		series_en = translator.translate(series_ru)

		guess_series = await self._guess_series(guess_brand.id, series_en)
		if not guess_series:
			raise GuessCommonCarInfoError(f'Не удалось определить модель марки {brand_en}: {series_ru} -> {series_en}')

		guess_generations = await self._guess_generations(guess_series.id, data.year)
		guess_trims = await self._guess_trims([it.id for it in guess_generations])

		return GuessCommonCarInfoSchema(
			brand=to_choice_field(guess_brand),
			model=to_choice_field(guess_series),
			generation=to_choice_field_list(guess_generations),
			configuration=to_choice_field_with_parent_list(guess_trims, 'generation'),
		)

	@classmethod
	async def _guess_brand(cls, brand_en: str) -> VehicleBrand | None:
		return await cls._fuzzy_lookup(VehicleBrand, brand_en)

	@classmethod
	async def _guess_series(cls, brand_id: UUID, model_en: str) -> VehicleSeries | None:
		return await cls._fuzzy_lookup(
			VehicleSeries,
			model_en,
			extra_where=VehicleSeries.brand_id == brand_id,
		)

	@staticmethod
	async def _guess_generations(series_id: UUID, car_production_year: int) -> list[VehicleGeneration]:
		guess_generation_query = select(VehicleGeneration).where(
			and_(
				VehicleGeneration.series_id == series_id,
				between(car_production_year, VehicleGeneration.start_year, VehicleGeneration.end_year),
			)
		)

		return await database.fetch_all(guess_generation_query)

	@staticmethod
	async def _guess_trims(generation_ids: list[UUID], **kwargs: None) -> list[CarTrim]:
		if not generation_ids:
			return []

		trim_query = (
			select(CarTrim)
			.where(CarTrim.generation_id.in_(generation_ids))
			.options(
				selectinload(CarTrim.generation)
			)
		)

		return await database.fetch_all(trim_query)

	@staticmethod
	async def _fuzzy_lookup(
			model: type[TFuzzyModel],
			query_text: str,
			extra_where: ColumnElement[bool] | None = None,
	) -> TFuzzyModel | None:
		"""
        Найти запись модели по полю ``name``.

        Сначала пробует точное совпадение через ``ILIKE``. Если такой записи нет,
        выполняет нечёткий поиск через PostgreSQL ``pg_trgm`` (функция ``similarity``).

        Защищает от ложных совпадений:

        1. Запросы короче ``MIN_FUZZY_QUERY_LENGTH`` символов не идут в trigram-поиск:
        на коротких строках similarity нестабилен.
        2. Если top-1 и top-2 кандидата неотличимы по score (разница меньше
        ``TRIGRAM_AMBIGUITY_EPS``), поднимается ``GuessCommonCarInfoError``,
        а не возвращается случайный.

        Метод требует, чтобы у ``model`` была колонка ``name``.
        """
		stripped_query = query_text.strip()

		name_column = cast(InstrumentedAttribute[str], getattr(model, 'name'))

		exact_filters: list[ColumnElement[bool]] = [name_column.ilike(stripped_query)]
		if extra_where is not None:
			exact_filters.append(extra_where)

		exact_match: TFuzzyModel | None = await database.fetch_one(select(model).where(*exact_filters))
		if exact_match is not None:
			return exact_match

		if len(stripped_query) < MIN_FUZZY_QUERY_LENGTH:
			return None

		similarity_expr = func.similarity(func.lower(name_column), func.lower(stripped_query))

		fuzzy_filters: list[ColumnElement[bool]] = [similarity_expr >= TRIGRAM_THRESHOLD]
		if extra_where is not None:
			fuzzy_filters.append(extra_where)

		fuzzy_query = (
			select(model, similarity_expr.label('score'))
			.where(*fuzzy_filters)
			.order_by(similarity_expr.desc())
			.limit(2)
		)

		async with database.get_async_session() as session:
			result = await session.execute(fuzzy_query)
			rows: list[tuple[TFuzzyModel, float]] = list(result.all())

		if not rows:
			return None

		if len(rows) == 1:
			return rows[0][0]

		top1, score1 = rows[0]
		top2, score2 = rows[1]
		if score1 - score2 >= TRIGRAM_AMBIGUITY_EPS:
			return top1

		top1_name = cast(str, getattr(top1, 'name'))
		top2_name = cast(str, getattr(top2, 'name'))
		raise GuessCommonCarInfoError(
			f'Неоднозначность для {query_text!r}: {top1_name} ({score1:.2f}) vs {top2_name} ({score2:.2f})'
		)
