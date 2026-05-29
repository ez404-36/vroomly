"""Сервис материализации узлов экземпляра ТС (``UserVehicleNode``).

При добавлении ТС в гараж пользователя его агрегаты (двигатель, КПП, кузов)
известны на уровне справочника — через ``CarSpec`` (заводская комплектация
``trim`` + опциональные свапы ``engine``/``transmission``). Чтобы к этим
агрегатам можно было привязывать пер-машинные события (напоминания, история
обслуживания), нужно материализовать экземпляры узлов — строки
``UserVehicleNode``, связывающие ``UserVehicle`` с конкретными ``VehicleNode``.

Сервис идемпотентен: повторный вызов не создаёт дубликатов (UNIQUE
``user_vehicle_id`` + ``vehicle_node_id``), а новые агрегаты досоздаёт.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from apps.vehicles.models.car.car_spec import CarSpec
from apps.vehicles.models.car.car_trim import CarTrim
from apps.vehicles.models.node.user_vehicle_node import UserVehicleNode
from apps.vehicles.models.vehicle.user_vehicle import UserVehicle
from core.db import database


class SyncUserVehicleNodes:
	"""Материализует ``UserVehicleNode`` для экземпляра ТС по его ``CarSpec``."""

	@classmethod
	async def for_user_vehicle(cls, user_vehicle_id: UUID) -> list[UserVehicleNode]:
		"""
		Создать недостающие ``UserVehicleNode`` для указанного ``UserVehicle``.

		Резолвит фактические агрегаты экземпляра (двигатель/КПП — с учётом свапа
		через ``effective_*``; кузов — из заводской комплектации ``trim``) и
		идемпотентно добавляет строки экземпляров узлов.

		:returns: актуальный список ``UserVehicleNode`` данного ТС.
		"""
		async with database.get_async_session() as session:
			spec = await cls._load_spec(session, user_vehicle_id)
			if spec is None:
				return []

			node_ids = cls._collect_node_ids(spec)
			if node_ids:
				await cls._upsert_nodes(session, user_vehicle_id, node_ids)
				await session.commit()

			return await cls._load_existing_nodes(session, user_vehicle_id)

	@staticmethod
	async def _load_spec(session: AsyncSession, user_vehicle_id: UUID) -> CarSpec | None:
		"""
		Загрузить ``CarSpec`` экземпляра вместе со связями для резолва агрегатов.

		``UserVehicle`` и ``CarSpec`` оба ссылаются на общий ``Vehicle`` через
		``vehicle_id``, поэтому спецификация резолвится по ``vehicle_id`` целевого
		``UserVehicle``.
		"""
		vehicle_id_query = select(UserVehicle.vehicle_id).where(UserVehicle.id == user_vehicle_id)
		vehicle_id = await database.session_fetch_one(session, vehicle_id_query)
		if vehicle_id is None:
			return None

		query = (
			select(CarSpec)
			.where(CarSpec.vehicle_id == vehicle_id)
			.options(
				selectinload(CarSpec.engine),
				selectinload(CarSpec.transmission),
				# trim.engine / trim.transmission нужны как fallback в effective_*,
				# поэтому грузим их заранее (иначе async-ленивая загрузка упадёт).
				selectinload(CarSpec.trim).selectinload(CarTrim.engine),
				selectinload(CarSpec.trim).selectinload(CarTrim.transmission),
			)
		)
		return await database.session_fetch_one(session, query)

	@staticmethod
	def _collect_node_ids(spec: CarSpec) -> set[UUID]:
		"""
		Собрать id фактических узлов экземпляра.

		Двигатель и КПП берутся через ``effective_*`` (свап имеет приоритет над
		заводским); кузов — из ``trim`` (свапа кузова в модели нет).
		"""
		node_ids: set[UUID] = set()

		effective_engine = spec.effective_engine
		if effective_engine is not None:
			node_ids.add(effective_engine.id)

		effective_transmission = spec.effective_transmission
		if effective_transmission is not None:
			node_ids.add(effective_transmission.id)

		if spec.trim is not None and spec.trim.body_id is not None:
			node_ids.add(spec.trim.body_id)

		return node_ids

	@staticmethod
	async def _upsert_nodes(session: AsyncSession, user_vehicle_id: UUID, node_ids: set[UUID]) -> None:
		"""Идемпотентно вставить экземпляры узлов (конфликт по UNIQUE игнорируется)."""
		rows = [{'user_vehicle_id': user_vehicle_id, 'vehicle_node_id': node_id} for node_id in node_ids]
		statement = insert(UserVehicleNode).values(rows).on_conflict_do_nothing(
			constraint='user_vehicle_node_unique',
		)
		await session.execute(statement)

	@staticmethod
	async def _load_existing_nodes(session: AsyncSession, user_vehicle_id: UUID) -> list[UserVehicleNode]:
		query = select(UserVehicleNode).where(UserVehicleNode.user_vehicle_id == user_vehicle_id)
		return list(await database.session_fetch_all(session, query))
