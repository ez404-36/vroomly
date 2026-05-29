from typing import TypeVar, cast
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy import ColumnElement, and_, between, func, select
from sqlalchemy.orm import InstrumentedAttribute, selectinload

from apps.vehicles.integrations.car_info_by_vin.schema import CarInfoByVinDataSchema
from apps.vehicles.models.car.car_trim import CarTrim
from apps.vehicles.models.car.enums import CarBodyType, CarDriveType
from apps.vehicles.models.node.body_node import CarBodyNode
from apps.vehicles.models.node.engine_node import EngineNode
from apps.vehicles.models.node.transmission_node import CarTransmissionNode
from apps.vehicles.models.vehicle.enums import VehicleEngineType, VehicleTransmissionType
from apps.vehicles.models.vehicle.vehicle_brand import VehicleBrand
from apps.vehicles.models.vehicle.vehicle_generation import VehicleGeneration
from apps.vehicles.models.vehicle.vehicle_series import VehicleSeries
from common.providers.translators.main import Translator
from common.schemas.choices_utils import to_choice_field, to_choice_field_list
from common.schemas.fields import (
	ChoiceFieldSchema,
	TrimChoiceSchema,
	TrimEngineSchema,
	TrimTransmissionSchema,
)
from core.db import database
from core.models import AutoSchemaBase

_ENGINE_TYPE_LABELS: dict[VehicleEngineType, str] = {
	VehicleEngineType.PETROL: 'Бензин',
	VehicleEngineType.DIESEL: 'Дизель',
	VehicleEngineType.ELECTRO: 'Электро',
	VehicleEngineType.GAS: 'Газ',
	VehicleEngineType.ATMOSPHERIC: 'Атмосферный',
	VehicleEngineType.TURBO: 'Турбо',
}

_TRANSMISSION_TYPE_LABELS: dict[VehicleTransmissionType, str] = {
	VehicleTransmissionType.MANUAL: 'МКПП',
	VehicleTransmissionType.AUTO: 'АКПП',
	VehicleTransmissionType.ROBOT: 'Робот',
	VehicleTransmissionType.VARIATOR: 'Вариатор',
}

_DRIVE_TYPE_LABELS: dict[CarDriveType, str] = {
	CarDriveType.FRONT: 'Передний',
	CarDriveType.BACK: 'Задний',
	CarDriveType.FULL: 'Полный',
}

_BODY_TYPE_LABELS: dict[CarBodyType, str] = {
	CarBodyType.SEDAN: 'Седан',
	CarBodyType.HATCHBACK: 'Хэтчбек',
	CarBodyType.SW: 'Универсал',
	CarBodyType.COUPE: 'Купе',
	CarBodyType.CUV: 'Кроссовер',
	CarBodyType.SUV: 'Внедорожник',
	CarBodyType.LIFTBACK: 'Лифтбек',
	CarBodyType.ROADSTER: 'Родстер',
	CarBodyType.VAN: 'Фургон',
	CarBodyType.MINIVAN: 'Минивэн',
	CarBodyType.PICKUP_TRUCK: 'Пикап',
	CarBodyType.MINIBUS: 'Микроавтобус',
	CarBodyType.TARGA: 'Тарга',
	CarBodyType.FASTBACK: 'Фастбэк',
	CarBodyType.LANDAU: 'Ландо',
	CarBodyType.CUV_COUPE: 'Кросс-купе',
	CarBodyType.SHOOTING_BRAKE: 'Шутинг-брейк',
}


def _engine_type_label(engine_type: VehicleEngineType | None) -> str | None:
	"""Собрать человекочитаемую строку из IntFlag-типа двигателя."""
	if not engine_type:
		return None
	parts = [label for flag, label in _ENGINE_TYPE_LABELS.items() if flag in engine_type]
	return ', '.join(parts) if parts else None


def _drive_type_label(drive_types: CarDriveType | list[CarDriveType] | None) -> str | None:
	"""Собрать строку из (возможно множественного) типа привода."""
	if not drive_types:
		return None
	values = drive_types if isinstance(drive_types, list) else [drive_types]
	parts = [_DRIVE_TYPE_LABELS[value] for value in values if value in _DRIVE_TYPE_LABELS]
	return ', '.join(parts) if parts else None

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
	generations: list[ChoiceFieldSchema] = Field(description='Поколение')
	trims: list[TrimChoiceSchema] = Field(description='Комплектация')


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
			generations=to_choice_field_list(guess_generations),
			trims=[self._serialize_trim(trim) for trim in guess_trims],
		)

	@staticmethod
	def _serialize_trim(trim: CarTrim) -> TrimChoiceSchema:
		"""Собрать ``TrimChoiceSchema`` с расширенными данными о комплектации.

		Формирует структурированные данные о двигателе/КПП/приводе/кузове и
		готовую человекочитаемую строку ``description`` для опции селектора,
		например: ``1.6 (110 л.с.) Бензин · АКПП 6 · Передний · Седан``.
		"""
		engine: EngineNode | None = trim.engine
		transmission: CarTransmissionNode | None = trim.transmission
		body: CarBodyNode | None = trim.body

		engine_type_label = _engine_type_label(engine.type) if engine is not None else None
		transmission_type_label = (
			_TRANSMISSION_TYPE_LABELS.get(transmission.type) if transmission is not None else None
		)
		drive_label = _drive_type_label(transmission.drive_types) if transmission is not None else None
		body_label = _BODY_TYPE_LABELS.get(body.type) if body is not None else None

		engine_schema: TrimEngineSchema | None = None
		if engine is not None:
			engine_schema = TrimEngineSchema(
				name=engine.name,
				volume=engine.volume,
				power=engine.power,
				type=engine_type_label,
				torque=engine.torque,
			)

		transmission_schema: TrimTransmissionSchema | None = None
		if transmission is not None:
			transmission_schema = TrimTransmissionSchema(
				name=transmission.name,
				type=transmission_type_label,
				gears=transmission.gears,
			)

		description_parts: list[str] = []
		if engine is not None:
			engine_part = f'{engine.volume / 1000:.1f}' if engine.volume else engine.name
			if engine.power:
				engine_part = f'{engine_part} ({engine.power} л.с.)'
			if engine_type_label:
				engine_part = f'{engine_part} {engine_type_label}'
			description_parts.append(engine_part)
		if transmission is not None:
			transmission_part = transmission_type_label or transmission.name
			if transmission.gears:
				transmission_part = f'{transmission_part} {transmission.gears}'
			description_parts.append(transmission_part)
		if drive_label:
			description_parts.append(drive_label)
		if body_label:
			description_parts.append(body_label)

		description = ' · '.join(description_parts) if description_parts else trim.name

		return TrimChoiceSchema(
			id=trim.id,
			name=trim.name,
			parent=to_choice_field(trim.generation),
			description=description,
			engine=engine_schema,
			transmission=transmission_schema,
			drive_type=drive_label,
			body_type=body_label,
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
				selectinload(CarTrim.generation),
				selectinload(CarTrim.engine),
				selectinload(CarTrim.transmission),
				selectinload(CarTrim.body),
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
