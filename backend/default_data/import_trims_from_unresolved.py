"""
Догенерация ``CarTrim``-объектов из ранее сохранённого
``default_data/parsed/trims_unresolved.json``.

Предполагается, что справочники ``vehicle_engine`` и ``car_transmission``
уже наполнены недостающими записями (см. ``missing_engines.json`` /
``missing_transmissions.json``) — например, через дополнительный прогон
otoba-парсера или ручной ввод.

Скрипт делает один пасс по списку «нерезолвнутых» trim-payload'ов:

1. Перечитывает справочники из БД (брендов, серий, поколений, двигателей,
   трансмиссий).
2. Для каждого payload'а пытается заново найти ``engine`` и ``transmission``
   по тем же candidate-именам, что использовались при первичном импорте.
3. Если оба узла нашлись — резолвит ``VehicleGeneration`` по натуральному
   ключу ``(series_id, name, is_restyling)``; при отсутствии — создаёт.
4. Создаёт ``CarTrim`` (с ``body_id=None`` и ``body_str`` из payload'а),
   дедуплицируя по ``(generation_id, engine_id, transmission_id, name,
   body_str)`` относительно уже существующих в БД записей.
5. Перевыгружает ``default_data/csv_files/{vehicle_generation,car_trim}.csv``,
   чтобы новые данные подхватывал ``seed_all.py``.
6. Пишет «остаток» (всё ещё не нашедшиеся payload'ы) в
   ``default_data/parsed/trims_unresolved.json`` — чтобы файл оставался
   актуальным состоянием очереди на добивание.

Запуск:

    docker compose run --rm backend-build python -m default_data.import_trims_from_unresolved
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from collections import defaultdict
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.vehicles.models.car.car_trim import CarTrim
from apps.vehicles.models.node.engine_node import EngineNode
from apps.vehicles.models.node.transmission_node import CarTransmissionNode
from apps.vehicles.models.vehicle.vehicle_brand import VehicleBrand
from apps.vehicles.models.vehicle.vehicle_generation import VehicleGeneration
from apps.vehicles.models.vehicle.vehicle_series import VehicleSeries
from core.db import database
from default_data.create_car_trims_from_pkl import (
	CSV_FILES_DIR,
	GEN_YEAR_MAX,
	GEN_YEAR_MIN,
	MISSING_ENGINES_JSON_PATH,
	MISSING_TRANSMISSIONS_JSON_PATH,
	UNRESOLVED_JSON_PATH,
	_coerce_name,
	_coerce_year,
	_export_table_to_csv,
	_write_missing_nodes_json,
	_write_unresolved_json,
)

logger = logging.getLogger('import_trims_from_unresolved')


class _NodeIndex:
	"""
	In-memory индекс справочников для быстрого резолва ``engine`` /
	``transmission`` / ``series`` / ``generation`` / ``brand``.

	Ключи приведены к тем же структурам, что в первичном импорте
	``create_car_trims_from_pkl``, чтобы поведение совпадало 1-в-1.
	"""

	def __init__(self) -> None:
		self.brand_by_id: dict[uuid.UUID, VehicleBrand] = {}
		self.series_ids: set[uuid.UUID] = set()
		# натуральный ключ generation -> уже существующая запись
		self.generation_by_key: dict[tuple[uuid.UUID, str, bool], VehicleGeneration] = {}

		self.engine_by_brand: dict[tuple[uuid.UUID, str], EngineNode] = {}
		self.engine_by_concern: dict[tuple[uuid.UUID, str], EngineNode] = {}
		self.transmission_by_brand: dict[tuple[uuid.UUID, str], CarTransmissionNode] = {}
		self.transmission_by_concern: dict[tuple[uuid.UUID, str], CarTransmissionNode] = {}

		# Существующие CarTrim'ы — для дедупликации.
		# Ключ — (generation_id, engine_id, transmission_id, name, body_str)
		self.existing_trim_keys: set[tuple[uuid.UUID, uuid.UUID, uuid.UUID, str, str | None]] = set()

	async def load(self, session: AsyncSession) -> None:
		brands = (await session.execute(select(VehicleBrand))).scalars().all()
		for brand in brands:
			self.brand_by_id[brand.id] = brand

		series_ids = (await session.execute(select(VehicleSeries.id))).scalars().all()
		self.series_ids = set(series_ids)

		generations = (await session.execute(select(VehicleGeneration))).scalars().all()
		for gen in generations:
			self.generation_by_key[(gen.series_id, gen.name, gen.is_restyling)] = gen

		engines = (await session.execute(select(EngineNode))).scalars().all()
		for engine in engines:
			if engine.brand_id is not None:
				self.engine_by_brand.setdefault((engine.brand_id, engine.name), engine)
			if engine.concern_id is not None:
				self.engine_by_concern.setdefault(
					(engine.concern_id, engine.name),
					engine,
				)

		transmissions = (await session.execute(select(CarTransmissionNode))).scalars().all()
		for transmission in transmissions:
			if transmission.brand_id is not None:
				self.transmission_by_brand.setdefault(
					(transmission.brand_id, transmission.name),
					transmission,
				)
			if transmission.concern_id is not None:
				self.transmission_by_concern.setdefault(
					(transmission.concern_id, transmission.name),
					transmission,
				)

		existing_trims = (await session.execute(select(CarTrim))).scalars().all()
		for trim in existing_trims:
			self.existing_trim_keys.add(
				(
					trim.generation_id,
					trim.engine_id,
					trim.transmission_id,
					trim.name,
					trim.body_str,
				)
			)

		logger.info(
			'Loaded: brands=%d, series=%d, generations=%d, engines=%d, transmissions=%d, existing_trims=%d',
			len(self.brand_by_id),
			len(self.series_ids),
			len(self.generation_by_key),
			len(engines),
			len(transmissions),
			len(self.existing_trim_keys),
		)

	def resolve_engine(
		self,
		brand: VehicleBrand,
		candidates: list[str],
	) -> EngineNode | None:
		for name in candidates:
			engine = self.engine_by_brand.get((brand.id, name))
			if engine is not None:
				return engine
			if brand.concern_id is not None:
				engine = self.engine_by_concern.get((brand.concern_id, name))
				if engine is not None:
					return engine
		return None

	def resolve_transmission(
		self,
		brand: VehicleBrand,
		candidates: list[str],
	) -> CarTransmissionNode | None:
		for name in candidates:
			transmission = self.transmission_by_brand.get((brand.id, name))
			if transmission is not None:
				return transmission
			if brand.concern_id is not None:
				transmission = self.transmission_by_concern.get(
					(brand.concern_id, name),
				)
				if transmission is not None:
					return transmission
		return None


def _parse_uuid(value: Any) -> uuid.UUID | None:
	if not isinstance(value, str) or not value:
		return None
	try:
		return uuid.UUID(value)
	except ValueError:
		return None


class _Importer:
	"""
	Обходит ``trims_unresolved.json``, добивая ``car_trim``-записи на
	свежеподнятых справочных данных.
	"""

	def __init__(self, session: AsyncSession, index: _NodeIndex) -> None:
		self.session = session
		self.index = index

		self.created_generations: list[VehicleGeneration] = []
		self.created_trims: list[CarTrim] = []
		self.still_unresolved: list[dict[str, Any]] = []
		self.skipped: dict[str, int] = defaultdict(int)

	def process(self, entries: list[dict[str, Any]]) -> None:
		for entry in entries:
			self._process_one(entry)

	def _process_one(self, entry: dict[str, Any]) -> None:
		brand_id = _parse_uuid(entry.get('brand_id'))
		if brand_id is None:
			self.skipped['no_brand_id'] += 1
			return
		brand = self.index.brand_by_id.get(brand_id)
		if brand is None:
			self.skipped['brand_not_in_db'] += 1
			return

		engine_candidates = entry.get('engine_candidates') or []
		transmission_candidates = entry.get('transmission_candidates') or []
		engine = self.index.resolve_engine(brand, engine_candidates)
		transmission = self.index.resolve_transmission(brand, transmission_candidates)

		# Один payload помечаем как «всё ещё не разрешён», если хотя бы один из
		# обязательных узлов всё ещё не найден.
		still_missing: list[str] = []
		if engine is None:
			still_missing.append('engine_not_found')
		if transmission is None:
			still_missing.append('transmission_not_found')
		if still_missing:
			new_entry = dict(entry)
			new_entry['reasons'] = still_missing
			self.still_unresolved.append(new_entry)
			for reason in still_missing:
				self.skipped[reason] += 1
			return

		# Сужение для type-checker'а: проверено выше.
		assert engine is not None
		assert transmission is not None

		generation = self._resolve_or_create_generation(entry)
		if generation is None:
			return

		raw_name = _coerce_name((entry.get('trim_payload') or {}).get('name')) or 'Standard'
		trim_name = raw_name[:50]
		raw_body = _coerce_name((entry.get('trim_payload') or {}).get('body'))
		body_str = raw_body[:50] if raw_body else None

		dedup_key = (
			generation.id,
			engine.id,
			transmission.id,
			trim_name,
			body_str,
		)
		if dedup_key in self.index.existing_trim_keys:
			self.skipped['already_exists'] += 1
			return

		trim = CarTrim(
			id=uuid.uuid4(),
			name=trim_name,
			options={},
			engine_id=engine.id,
			transmission_id=transmission.id,
			generation_id=generation.id,
			body_id=None,
			body_str=body_str,
			avg_fuel_consumption=None,
			acceleration=None,
			clearance=None,
		)
		self.created_trims.append(trim)
		# Защищаемся от дубликатов внутри одного запуска тоже.
		self.index.existing_trim_keys.add(dedup_key)

	def _resolve_or_create_generation(
		self,
		entry: dict[str, Any],
	) -> VehicleGeneration | None:
		gen_payload = entry.get('generation') or {}
		series_id = _parse_uuid(gen_payload.get('series_id'))
		if series_id is None or series_id not in self.index.series_ids:
			self.skipped['series_not_in_db'] += 1
			return None

		raw_name = _coerce_name(gen_payload.get('name')) or '1'
		gen_name = raw_name[:50]
		is_restyling = bool(gen_payload.get('is_restyling'))

		key = (series_id, gen_name, is_restyling)
		existing = self.index.generation_by_key.get(key)
		if existing is not None:
			return existing

		start_year = _coerce_year(gen_payload.get('start_year'))
		if start_year is None:
			self.skipped['invalid_start_year'] += 1
			return None
		end_year = _coerce_year(gen_payload.get('end_year'))
		if end_year is not None and end_year < start_year:
			end_year = None
		# Дополнительный sanity-check.
		if not (GEN_YEAR_MIN <= start_year <= GEN_YEAR_MAX):
			self.skipped['invalid_start_year'] += 1
			return None

		generation = VehicleGeneration(
			id=uuid.uuid4(),
			series_id=series_id,
			name=gen_name,
			is_restyling=is_restyling,
			start_year=start_year,
			end_year=end_year,
		)
		self.created_generations.append(generation)
		self.index.generation_by_key[key] = generation
		return generation

	async def flush(self) -> None:
		if self.created_generations:
			self.session.add_all(self.created_generations)
			await self.session.flush()
			logger.info('Создано поколений: %d', len(self.created_generations))
		if self.created_trims:
			self.session.add_all(self.created_trims)
			await self.session.flush()
			logger.info('Создано комплектаций: %d', len(self.created_trims))


async def main() -> None:
	"""Точка входа: trims_unresolved.json → довсыпка CarTrim → CSV-перевыгрузка."""
	logging.basicConfig(
		level=logging.INFO,
		format='%(asctime)s %(levelname)s %(name)s: %(message)s',
	)

	if not UNRESOLVED_JSON_PATH.exists():
		raise FileNotFoundError(
			f'Не найден файл {UNRESOLVED_JSON_PATH}. Сначала прогоните '
			f'`python -m default_data.create_car_trims_from_pkl`.'
		)

	with open(UNRESOLVED_JSON_PATH, encoding='utf-8') as fp:
		unresolved_payload = json.load(fp)

	entries: list[dict[str, Any]] = list(unresolved_payload.get('items', []))
	logger.info('Считано unresolved-записей: %d', len(entries))

	async with database.get_async_session() as session:
		index = _NodeIndex()
		await index.load(session)

		importer = _Importer(session, index)
		importer.process(entries)
		await importer.flush()
		await session.commit()

		for reason, count in sorted(importer.skipped.items()):
			logger.info('  %s: %d', reason, count)

		# Перевыгружаем CSV-сиды и обновляем JSON «остатка» + сводки по узлам.
		gen_csv = CSV_FILES_DIR / 'vehicle_generation.csv'
		trim_csv = CSV_FILES_DIR / 'car_trim.csv'
		gen_count = await _export_table_to_csv(session, VehicleGeneration, gen_csv)
		trim_count = await _export_table_to_csv(session, CarTrim, trim_csv)
		logger.info('Выгружено в %s: %d строк', gen_csv, gen_count)
		logger.info('Выгружено в %s: %d строк', trim_csv, trim_count)

		_write_unresolved_json(importer.still_unresolved, UNRESOLVED_JSON_PATH)
		_write_missing_nodes_json(
			importer.still_unresolved,
			MISSING_ENGINES_JSON_PATH,
			reason='engine_not_found',
			candidates_key='engine_candidates',
			label='двигателей',
		)
		_write_missing_nodes_json(
			importer.still_unresolved,
			MISSING_TRANSMISSIONS_JSON_PATH,
			reason='transmission_not_found',
			candidates_key='transmission_candidates',
			label='трансмиссий',
		)


if __name__ == '__main__':
	asyncio.run(main())
