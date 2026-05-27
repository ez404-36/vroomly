"""
Создание объектов CarTrim и VehicleGeneration из ``parsed/trims.pkl``.

Файл ``trims.pkl`` создан парсером otoba.ru (см.
``default_data/parsers/html_parsers/otoba/parser.py``). Внутри —
сырые ответы LLM в формате markdown-обёртки ```json … ``` (по одному ответу
на страницу-поколение). Каждый ответ содержит описание одного или нескольких
поколений модели и список комплектаций каждого поколения.

Скрипт:

1. Парсит pkl-файл, чинит локальные синтаксические артефакты LLM
   (висячие запятые, ``//`` комментарии, плейсхолдеры годов вида ``202X``).
2. Создаёт ``VehicleGeneration`` по (бренд, серия, имя, годы, рестайл).
3. Создаёт ``CarTrim`` со ссылками на ``engine``, ``transmission`` и
   ``generation``. Кузов сохраняется в текстовом виде в ``CarTrim.body_str``
   (справочник ``CarBody`` пока не наполнен — ``body_id`` остаётся ``None``).
4. После успешной вставки экспортирует ``vehicle_generation.csv`` и
   ``car_trim.csv`` в ``default_data/csv_files/``, чтобы дальше эти данные
   подхватывал ``seed_all.py``.
5. Параллельно выгружает в ``default_data/parsed/trims_unresolved.json`` все
   trim-payload'ы из pkl, для которых не нашёлся ``engine`` или
   ``transmission`` в БД — для последующего ручного разбора/допарсинга.
6. На основе того же сырого списка генерирует агрегированные сводки
   ``default_data/parsed/missing_engines.json`` и
   ``default_data/parsed/missing_transmissions.json`` — уникальные пары
   ``(brand_id, name)`` с привязкой к бренду/концерну. Удобно скармливать
   парсеру/ручному импорту для добивания справочников.

Запуск:

    docker compose run --rm backend-build python -m default_data.create_car_trims_from_pkl
"""

from __future__ import annotations

import asyncio
import csv
import json
import logging
import pickle
import re
import uuid
from collections import defaultdict
from pathlib import Path
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.vehicles.models.car.car_transmission import CarTransmission
from apps.vehicles.models.car.car_trim import CarTrim
from apps.vehicles.models.vehicle.vehicle_brand import VehicleBrand
from apps.vehicles.models.vehicle.vehicle_engine import VehicleEngine
from apps.vehicles.models.vehicle.vehicle_generation import VehicleGeneration
from apps.vehicles.models.vehicle.vehicle_series import VehicleSeries
from common.utils.generators import generate_code
from core.constants import BACKEND_DIR
from core.db import database
from core.models import AutoSchemaBase

logger = logging.getLogger('create_car_trims_from_pkl')

PARSED_DATA_DIR = BACKEND_DIR / 'default_data' / 'parsed'
CSV_FILES_DIR = BACKEND_DIR / 'default_data' / 'csv_files'
PKL_PATH = PARSED_DATA_DIR / 'trims.pkl'
UNRESOLVED_JSON_PATH = PARSED_DATA_DIR / 'trims_unresolved.json'
MISSING_ENGINES_JSON_PATH = PARSED_DATA_DIR / 'missing_engines.json'
MISSING_TRANSMISSIONS_JSON_PATH = PARSED_DATA_DIR / 'missing_transmissions.json'

GEN_YEAR_MIN = 1885
GEN_YEAR_MAX = 2100

# Маппер концернов и брендов, аналогичный otoba-парсеру.
# Когда LLM возвращает имя бренда/концерна, оно может расходиться с тем,
# что лежит в БД, — нормализуем заранее.
CONCERN_CODE_OVERRIDES = {
    'HYUNDAI_KIA': 'HYUNDAI_MG',
}
BRAND_CODE_OVERRIDES = {
    'MERCEDES': 'MERCEDES_BENZ',
}


def _normalize_brand_code(raw: str) -> str:
    code = generate_code(raw)
    return BRAND_CODE_OVERRIDES.get(code, CONCERN_CODE_OVERRIDES.get(code, code))


def _strip_markdown_json_fence(raw: str) -> str:
    """Удаляет markdown-обёртку ```json … ``` если она есть."""
    stripped = raw.strip()
    fence = re.match(r'^```(?:json)?\s*\n?(.*?)\n?```\s*$', stripped, re.DOTALL)
    if fence:
        return fence.group(1).strip()
    return stripped


def _fix_llm_json_artifacts(raw: str) -> str:
    """
    Чинит локальные синтаксические погрешности LLM:

    - JS-style комментарии ``// ...`` (живут отдельной строкой);
    - висячие запятые перед ``}`` или ``]``;
    - плейсхолдеры годов вида ``202X``/``20XX`` → ``null``.

    Эти ошибки наблюдались в trims.pkl на индексах 90, 809, 874.
    """
    # 1) Удаляем `// ...` до конца строки (LLM иногда поясняет пропуски).
    cleaned = re.sub(r'//[^\n]*', '', raw)
    # 2) Плейсхолдеры годов: ":  202X" / ":  20XX" → ": null".
    cleaned = re.sub(r':\s*\d+[Xx]+(?=\s*[,}\]])', ': null', cleaned)
    # 3) Висячие запятые перед `}` или `]`.
    cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
    return cleaned


def _parse_llm_response(raw: str) -> list[dict] | None:
    """
    Возвращает список ``{'generation': {...}, 'trims': [...]}`` из одного
    ответа LLM. ``None`` — если распарсить не удалось даже после фиксов.
    """
    payload = _fix_llm_json_artifacts(_strip_markdown_json_fence(raw))
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError as exc:
        logger.warning('Не удалось распарсить ответ LLM: %s', exc)
        return None

    if isinstance(parsed, dict):
        return [parsed]
    if isinstance(parsed, list):
        return [item for item in parsed if isinstance(item, dict)]
    return None


def _coerce_year(value: Any) -> int | None:
    """Парсит год в диапазоне допустимых значений ``VehicleGeneration``."""
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        year = value
    elif isinstance(value, str):
        match = re.search(r'\d{4}', value)
        if not match:
            return None
        year = int(match.group())
    else:
        return None
    if GEN_YEAR_MIN <= year <= GEN_YEAR_MAX:
        return year
    return None


def _coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {'true', 't', '1', 'yes', 'y'}
    return False


def _coerce_name(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    return cleaned or None


def _coerce_name_candidates(value: Any) -> list[str]:
    """
    Возвращает список строковых кандидатов из произвольного значения.

    LLM иногда отдаёт ``transmission`` массивом (например, ``["M32",
    "Selespeed"]``) или строкой ``"M32, Selespeed"`` — для надёжного резолва
    разворачиваем такие случаи в отдельные имена.
    """
    if value is None:
        return []
    if isinstance(value, list):
        candidates: list[str] = []
        for item in value:
            candidates.extend(_coerce_name_candidates(item))
        return candidates
    if isinstance(value, str):
        return [part.strip() for part in value.split(',') if part.strip()]
    return []


class CarTrimBuilder:
    """
    Заполняет БД поколениями и комплектациями из pkl-файла, попутно собирая
    статистику пропусков для отчётности.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

        self._brand_by_code: dict[str, VehicleBrand] = {}
        # (brand_id, series_name_lower) -> VehicleSeries
        self._series_by_brand_name: dict[tuple[uuid.UUID, str], VehicleSeries] = {}
        # (engine_name, brand_id|None, concern_id|None) -> VehicleEngine
        self._engines_by_brand: dict[tuple[uuid.UUID, str], VehicleEngine] = {}
        self._engines_by_concern: dict[tuple[uuid.UUID, str], VehicleEngine] = {}
        self._transmissions_by_brand: dict[tuple[uuid.UUID, str], CarTransmission] = {}
        self._transmissions_by_concern: dict[tuple[uuid.UUID, str], CarTransmission] = {}

        self.generations: list[VehicleGeneration] = []
        # дедуп по (series_id, name, is_restyling) — уникальный констрейнт в БД
        self._generation_keys: set[tuple[uuid.UUID, str, bool]] = set()
        self.trims: list[CarTrim] = []

        self.skipped: dict[str, int] = defaultdict(int)
        # Сырые trim-payload'ы, для которых не нашлись engine или transmission,
        # сгруппированные по бренду + поколению. Эту информацию выгружаем в
        # отдельный JSON, чтобы можно было либо допарсить недостающие узлы,
        # либо вручную создать соответствующие справочные записи.
        self.unresolved: list[dict[str, Any]] = []

    async def prefetch(self) -> None:
        brands = (await self.session.execute(select(VehicleBrand))).scalars().all()
        for brand in brands:
            self._brand_by_code[brand.code] = brand
            if brand.abbreviation:
                # Не перетираем существующий маппинг по code, только дополняем.
                self._brand_by_code.setdefault(brand.abbreviation, brand)

        series_list = (await self.session.execute(select(VehicleSeries))).scalars().all()
        for series in series_list:
            self._series_by_brand_name[(series.brand_id, series.name.lower())] = series

        engines = (await self.session.execute(select(VehicleEngine))).scalars().all()
        for engine in engines:
            if engine.brand_id is not None:
                self._engines_by_brand.setdefault((engine.brand_id, engine.name), engine)
            if engine.concern_id is not None:
                self._engines_by_concern.setdefault((engine.concern_id, engine.name), engine)

        transmissions = (await self.session.execute(select(CarTransmission))).scalars().all()
        for transmission in transmissions:
            if transmission.brand_id is not None:
                self._transmissions_by_brand.setdefault(
                    (transmission.brand_id, transmission.name), transmission,
                )
            if transmission.concern_id is not None:
                self._transmissions_by_concern.setdefault(
                    (transmission.concern_id, transmission.name), transmission,
                )

        logger.info(
            'Prefetched: brands=%d, series=%d, engines=%d, transmissions=%d',
            len(self._brand_by_code), len(self._series_by_brand_name),
            len(engines), len(transmissions),
        )

    def _resolve_brand(self, raw_name: str | None) -> VehicleBrand | None:
        if not raw_name:
            return None
        return self._brand_by_code.get(_normalize_brand_code(raw_name))

    def _resolve_series(
        self, brand: VehicleBrand, raw_series_name: str | None,
    ) -> VehicleSeries | None:
        if not raw_series_name:
            return None
        key = (brand.id, raw_series_name.strip().lower())
        return self._series_by_brand_name.get(key)

    def _resolve_engine(
        self, brand: VehicleBrand, candidates: list[str],
    ) -> VehicleEngine | None:
        for name in candidates:
            # Сначала пытаемся найти в рамках бренда, затем — в рамках концерна.
            engine = self._engines_by_brand.get((brand.id, name))
            if engine is not None:
                return engine
            if brand.concern_id is not None:
                engine = self._engines_by_concern.get((brand.concern_id, name))
                if engine is not None:
                    return engine
        return None

    def _resolve_transmission(
        self, brand: VehicleBrand, candidates: list[str],
    ) -> CarTransmission | None:
        for name in candidates:
            transmission = self._transmissions_by_brand.get((brand.id, name))
            if transmission is not None:
                return transmission
            if brand.concern_id is not None:
                transmission = self._transmissions_by_concern.get(
                    (brand.concern_id, name),
                )
                if transmission is not None:
                    return transmission
        return None

    def process_entries(self, entries: list[dict]) -> None:
        for entry in entries:
            generation_payload = entry.get('generation')
            if not isinstance(generation_payload, dict):
                self.skipped['no_generation'] += 1
                continue

            brand = self._resolve_brand(generation_payload.get('brand'))
            if brand is None:
                self.skipped['brand_not_found'] += 1
                continue

            series = self._resolve_series(brand, generation_payload.get('series'))
            if series is None:
                self.skipped['series_not_found'] += 1
                continue

            start_year = _coerce_year(generation_payload.get('start_year'))
            if start_year is None:
                # start_year — NOT NULL и обязан попадать в check-диапазон.
                self.skipped['invalid_start_year'] += 1
                continue
            end_year = _coerce_year(generation_payload.get('end_year'))
            if end_year is not None and end_year < start_year:
                end_year = None

            raw_gen_name = _coerce_name(generation_payload.get('name')) or '1'
            # name VARCHAR(50)
            gen_name = raw_gen_name[:50]
            is_restyling = _coerce_bool(generation_payload.get('is_restyling'))

            dedup_key = (series.id, gen_name, is_restyling)
            if dedup_key in self._generation_keys:
                # уже создавали такое же поколение в этом же запуске
                generation = next(
                    g for g in self.generations
                    if g.series_id == series.id
                    and g.name == gen_name
                    and g.is_restyling == is_restyling
                )
            else:
                generation = VehicleGeneration(
                    id=uuid.uuid4(),
                    series_id=series.id,
                    name=gen_name,
                    is_restyling=is_restyling,
                    start_year=start_year,
                    end_year=end_year,
                )
                self.generations.append(generation)
                self._generation_keys.add(dedup_key)

            trims_payload = entry.get('trims')
            if not isinstance(trims_payload, list):
                continue

            for trim_payload in trims_payload:
                if not isinstance(trim_payload, dict):
                    continue
                self._build_trim(brand, generation, trim_payload)

    def _build_trim(
        self,
        brand: VehicleBrand,
        generation: VehicleGeneration,
        payload: dict,
    ) -> None:
        engine_candidates = _coerce_name_candidates(payload.get('engine'))
        engine = self._resolve_engine(brand, engine_candidates)
        transmission_candidates = _coerce_name_candidates(payload.get('transmission'))
        transmission = self._resolve_transmission(brand, transmission_candidates)

        # Один trim может одновременно не найти и двигатель, и трансмиссию —
        # фиксируем оба факта в одной записи, чтобы не дублировать payload.
        missing_reasons: list[str] = []
        if engine is None:
            missing_reasons.append('engine_not_found')
            self.skipped['engine_not_found'] += 1
        if transmission is None:
            missing_reasons.append('transmission_not_found')
            self.skipped['transmission_not_found'] += 1

        if missing_reasons:
            self.unresolved.append({
                'reasons': missing_reasons,
                'brand_code': brand.code,
                'brand_id': str(brand.id),
                'concern_id': (
                    str(brand.concern_id) if brand.concern_id is not None else None
                ),
                'generation': {
                    'series_id': str(generation.series_id),
                    'name': generation.name,
                    'is_restyling': generation.is_restyling,
                    'start_year': generation.start_year,
                    'end_year': generation.end_year,
                },
                'engine_candidates': engine_candidates,
                'transmission_candidates': transmission_candidates,
                'trim_payload': payload,
            })
            return

        # Сужение для type-checker: после ветки выше оба гарантированно не None.
        assert engine is not None
        assert transmission is not None

        raw_name = _coerce_name(payload.get('name')) or 'Standard'
        trim_name = raw_name[:50]

        raw_body = _coerce_name(payload.get('body'))
        body_str = raw_body[:50] if raw_body else None

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
        self.trims.append(trim)

    async def flush(self) -> None:
        if self.generations:
            self.session.add_all(self.generations)
            await self.session.flush()
            logger.info('Вставлено поколений: %d', len(self.generations))
        if self.trims:
            self.session.add_all(self.trims)
            await self.session.flush()
            logger.info('Вставлено комплектаций: %d', len(self.trims))


def _row_to_csv(instance: AutoSchemaBase) -> dict[str, Any]:
    """Возвращает плоский dict значений колонок таблицы."""
    row: dict[str, Any] = {}
    for column in instance.get_table_columns():
        value = getattr(instance, column.name)
        if value is None:
            row[column.name] = ''
        elif isinstance(value, bool):
            row[column.name] = 't' if value else 'f'
        elif isinstance(value, uuid.UUID):
            row[column.name] = str(value)
        else:
            row[column.name] = value
    return row


async def _export_table_to_csv(
    session: AsyncSession,
    model: type[AutoSchemaBase],
    target_path: Path,
) -> int:
    """Выгружает все строки таблицы в CSV (с учётом UUID и булевых полей)."""
    rows = (await session.execute(select(model))).scalars().all()
    columns = [column.name for column in model.get_table_columns()]
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, 'w', newline='') as fp:
        writer = csv.DictWriter(fp, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(_row_to_csv(row))
    return len(rows)


def _write_unresolved_json(entries: list[dict[str, Any]], target_path: Path) -> None:
    """
    Выгружает все trim-payload'ы, для которых не нашёлся ``engine`` или
    ``transmission``, в JSON для последующего ручного разбора.

    Структура:

    ::

        {
            "total": <int>,
            "by_reason": {"engine_not_found": <int>, "transmission_not_found": <int>},
            "items": [
                {
                    "reasons": ["engine_not_found", "transmission_not_found"],
                    "brand_code": "TOYOTA",
                    "brand_id": "<uuid>",
                    "concern_id": "<uuid>|null",
                    "generation": {...},
                    "engine_candidates": ["..."],
                    "transmission_candidates": ["..."],
                    "trim_payload": {<сырой dict из pkl>}
                },
                ...
            ]
        }
    """
    by_reason: dict[str, int] = defaultdict(int)
    for entry in entries:
        for reason in entry.get('reasons', []):
            by_reason[reason] += 1

    payload = {
        'total': len(entries),
        'by_reason': dict(by_reason),
        'items': entries,
    }

    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, 'w', encoding='utf-8') as fp:
        json.dump(payload, fp, ensure_ascii=False, indent=2)
    logger.info('Выгружено нераспознанных trim-payload в %s: %d', target_path, len(entries))


def _write_missing_nodes_json(
    unresolved_entries: list[dict[str, Any]],
    target_path: Path,
    *,
    reason: str,
    candidates_key: str,
    label: str,
) -> None:
    """
    Агрегирует уникальные имена узлов (двигателей/трансмиссий), не нашедшихся
    в БД, с привязкой к бренду / концерну.

    Ключ дедупликации — ``(brand_id, name)`` (бренд — основная единица скоупа
    для движков/трансмиссий, концерн прикладывается информационно). ``name``
    из ``candidates_key`` берётся как есть, без нормализации, потому что в БД
    лежат именно «как написано в pkl».

    Структура файла:

    ::

        {
            "total": <int>,                    // уникальных (brand_id, name) пар
            "items": [
                {
                    "name": "AR37203",
                    "brand_code": "ALFA_ROMEO",
                    "brand_id": "<uuid>",
                    "concern_id": "<uuid>|null"
                },
                ...
            ]
        }
    """
    # Ключ — (brand_id, name); значение — единственный накопитель полей.
    aggregated: dict[tuple[str, str], dict[str, Any]] = {}
    for entry in unresolved_entries:
        if reason not in entry.get('reasons', ()):
            continue
        brand_id = entry.get('brand_id')
        if not brand_id:
            continue
        for raw_name in entry.get(candidates_key, ()) or ():
            name = (raw_name or '').strip()
            if not name:
                continue
            key = (brand_id, name)
            if key not in aggregated:
                aggregated[key] = {
                    'name': name,
                    'brand_code': entry.get('brand_code'),
                    'brand_id': brand_id,
                    'concern_id': entry.get('concern_id'),
                }

    # Сортируем для стабильного вывода: сначала по brand_code, потом по name.
    items = sorted(
        aggregated.values(),
        key=lambda it: (it['brand_code'] or '', it['name']),
    )

    payload = {
        'total': len(items),
        'items': items,
    }
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, 'w', encoding='utf-8') as fp:
        json.dump(payload, fp, ensure_ascii=False, indent=2)
    logger.info('Выгружено уникальных %s в %s: %d', label, target_path, len(items))


async def main() -> None:
    """Точка входа: pkl → БД → CSV-выгрузки для дальнейшего сидинга."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    )

    if not PKL_PATH.exists():
        raise FileNotFoundError(f'Не найден файл {PKL_PATH}')

    with open(PKL_PATH, 'rb') as f_obj:
        pkl_data = pickle.load(f_obj)

    raw_responses = pkl_data.get('vehicles', [])
    logger.info('Считано записей из pkl: %d', len(raw_responses))

    parsed_entries: list[dict] = []
    parse_failures = 0
    for raw in raw_responses:
        if not isinstance(raw, str):
            continue
        entries = _parse_llm_response(raw)
        if entries is None:
            parse_failures += 1
            continue
        parsed_entries.extend(entries)
    logger.info(
        'Распарсено: %d/%d (нераспознанных: %d), сущностей-поколений: %d',
        len(raw_responses) - parse_failures, len(raw_responses),
        parse_failures, len(parsed_entries),
    )

    async with database.get_async_session() as session:
        # Чистим предыдущий результат, чтобы скрипт был идемпотентным.
        # car_trim удаляем первым (FK на vehicle_generation).
        await session.execute(delete(CarTrim))
        await session.execute(delete(VehicleGeneration))
        await session.flush()

        builder = CarTrimBuilder(session)
        await builder.prefetch()
        builder.process_entries(parsed_entries)
        await builder.flush()
        await session.commit()

        for reason, count in sorted(builder.skipped.items()):
            logger.info('  пропущено (%s): %d', reason, count)

        _write_unresolved_json(builder.unresolved, UNRESOLVED_JSON_PATH)
        _write_missing_nodes_json(
            builder.unresolved, MISSING_ENGINES_JSON_PATH,
            reason='engine_not_found',
            candidates_key='engine_candidates',
            label='двигателей',
        )
        _write_missing_nodes_json(
            builder.unresolved, MISSING_TRANSMISSIONS_JSON_PATH,
            reason='transmission_not_found',
            candidates_key='transmission_candidates',
            label='трансмиссий',
        )

        gen_csv = CSV_FILES_DIR / 'vehicle_generation.csv'
        trim_csv = CSV_FILES_DIR / 'car_trim.csv'
        gen_count = await _export_table_to_csv(session, VehicleGeneration, gen_csv)
        trim_count = await _export_table_to_csv(session, CarTrim, trim_csv)
        logger.info('Выгружено в %s: %d строк', gen_csv, gen_count)
        logger.info('Выгружено в %s: %d строк', trim_csv, trim_count)


if __name__ == '__main__':
    asyncio.run(main())
