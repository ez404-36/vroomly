"""Нечёткий (trigram) поиск записей по полю ``name``.

Слой доступа к данным для подбора бренда/модели по переведённому названию.
Сначала пробует точное совпадение (``ILIKE``), затем PostgreSQL ``pg_trgm``
(``similarity``). Возвращает запись или ``None``; при неоднозначности top-1/top-2
поднимает ``GuessCommonCarInfoError`` (доменная ошибка подбора).
"""

from typing import TypeVar, cast

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.orm import InstrumentedAttribute

from core.db import database
from core.models import AutoSchemaBase

TRIGRAM_THRESHOLD: float = 0.3
TRIGRAM_AMBIGUITY_EPS: float = 0.05
MIN_FUZZY_QUERY_LENGTH: int = 3

TFuzzyModel = TypeVar('TFuzzyModel', bound=AutoSchemaBase)


class GuessCommonCarInfoError(Exception):
	"""Ошибка подбора данных ТС (марка/модель не определены или неоднозначны)."""


async def fuzzy_lookup(
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

	Требует, чтобы у ``model`` была колонка ``name``.
	"""
	stripped_query = query_text.strip()
	name_column = cast(InstrumentedAttribute[str], model.name)

	exact_match = await _find_exact(model, name_column, stripped_query, extra_where)
	if exact_match is not None:
		return exact_match

	if len(stripped_query) < MIN_FUZZY_QUERY_LENGTH:
		return None

	return await _find_fuzzy(model, name_column, stripped_query, extra_where, query_text)


async def _find_exact(
	model: type[TFuzzyModel],
	name_column: InstrumentedAttribute[str],
	stripped_query: str,
	extra_where: ColumnElement[bool] | None,
) -> TFuzzyModel | None:
	"""Точное совпадение по ``ILIKE``."""
	filters: list[ColumnElement[bool]] = [name_column.ilike(stripped_query)]
	if extra_where is not None:
		filters.append(extra_where)
	return await database.fetch_one(select(model).where(*filters))


async def _find_fuzzy(
	model: type[TFuzzyModel],
	name_column: InstrumentedAttribute[str],
	stripped_query: str,
	extra_where: ColumnElement[bool] | None,
	original_query: str,
) -> TFuzzyModel | None:
	"""Trigram-поиск top-2 кандидатов с защитой от неоднозначности."""
	similarity_expr = func.similarity(func.lower(name_column), func.lower(stripped_query))

	filters: list[ColumnElement[bool]] = [similarity_expr >= TRIGRAM_THRESHOLD]
	if extra_where is not None:
		filters.append(extra_where)

	fuzzy_query = (
		select(model, similarity_expr.label('score'))
		.where(*filters)
		.order_by(similarity_expr.desc())
		.limit(2)
	)

	async with database.get_async_session() as session:
		result = await session.execute(fuzzy_query)
		rows: list[tuple[TFuzzyModel, float]] = [(row[0], row[1]) for row in result.all()]

	if not rows:
		return None

	if len(rows) == 1:
		return rows[0][0]

	top1, score1 = rows[0]
	top2, score2 = rows[1]
	if score1 - score2 >= TRIGRAM_AMBIGUITY_EPS:
		return top1

	top1_name = cast(str, top1.name)
	top2_name = cast(str, top2.name)
	raise GuessCommonCarInfoError(
		f'Неоднозначность для {original_query!r}: {top1_name} ({score1:.2f}) vs {top2_name} ({score2:.2f})'
	)
