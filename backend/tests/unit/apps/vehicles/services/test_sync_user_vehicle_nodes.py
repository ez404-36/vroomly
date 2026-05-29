"""Tests for SyncUserVehicleNodes — материализация UserVehicleNode по CarSpec."""

import asyncio
from typing import Any, Coroutine, TypeVar
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

from apps.vehicles.models.car.car_spec import CarSpec
from apps.vehicles.models.car.car_trim import CarTrim
from apps.vehicles.models.node.body_node import CarBodyNode
from apps.vehicles.models.node.engine_node import EngineNode
from apps.vehicles.models.node.transmission_node import CarTransmissionNode
from apps.vehicles.services.sync_user_vehicle_nodes import SyncUserVehicleNodes

T = TypeVar('T')


def _run(coro: Coroutine[Any, Any, T]) -> T:
	"""Запускает корутину в свежем event loop (как в остальных unit-тестах сервисов)."""
	return asyncio.run(coro)


def _make_engine() -> Any:
	stub = MagicMock(spec=EngineNode)
	stub.id = uuid4()
	return stub


def _make_transmission() -> Any:
	stub = MagicMock(spec=CarTransmissionNode)
	stub.id = uuid4()
	return stub


def _make_body() -> Any:
	stub = MagicMock(spec=CarBodyNode)
	stub.id = uuid4()
	return stub


def _make_trim(engine: Any, transmission: Any, body_id: UUID | None) -> Any:
	stub = MagicMock(spec=CarTrim)
	stub.id = uuid4()
	stub.engine = engine
	stub.transmission = transmission
	stub.body_id = body_id
	return stub


def _make_spec(
	*,
	trim_engine: Any,
	trim_transmission: Any,
	trim_body_id: UUID | None,
	swap_engine: Any = None,
	swap_transmission: Any = None,
) -> Any:
	"""
	Строит заглушку CarSpec с реальной логикой ``effective_*``.

	Свап (``swap_engine``/``swap_transmission``) имеет приоритет над заводским
	двигателем/КПП из ``trim`` — повторяет поведение свойств модели.
	"""
	spec = MagicMock(spec=CarSpec)
	spec.trim = _make_trim(trim_engine, trim_transmission, trim_body_id)

	spec.engine = swap_engine
	spec.engine_id = swap_engine.id if swap_engine is not None else None
	spec.transmission = swap_transmission
	spec.transmission_id = swap_transmission.id if swap_transmission is not None else None

	spec.effective_engine = swap_engine if swap_engine is not None else trim_engine
	spec.effective_transmission = swap_transmission if swap_transmission is not None else trim_transmission
	return spec


class TestCollectNodeIds:
	"""Резолв id фактических узлов экземпляра (через ``_collect_node_ids``)."""

	def test_factory_config_collects_engine_transmission_body(self) -> None:
		engine = _make_engine()
		transmission = _make_transmission()
		body = _make_body()
		spec = _make_spec(
			trim_engine=engine,
			trim_transmission=transmission,
			trim_body_id=body.id,
		)

		node_ids = SyncUserVehicleNodes._collect_node_ids(spec)

		assert node_ids == {engine.id, transmission.id, body.id}

	def test_swap_engine_takes_priority_over_trim(self) -> None:
		trim_engine = _make_engine()
		swap_engine = _make_engine()
		transmission = _make_transmission()
		spec = _make_spec(
			trim_engine=trim_engine,
			trim_transmission=transmission,
			trim_body_id=None,
			swap_engine=swap_engine,
		)

		node_ids = SyncUserVehicleNodes._collect_node_ids(spec)

		assert swap_engine.id in node_ids
		assert trim_engine.id not in node_ids
		assert transmission.id in node_ids

	def test_swap_transmission_takes_priority_over_trim(self) -> None:
		engine = _make_engine()
		trim_transmission = _make_transmission()
		swap_transmission = _make_transmission()
		spec = _make_spec(
			trim_engine=engine,
			trim_transmission=trim_transmission,
			trim_body_id=None,
			swap_transmission=swap_transmission,
		)

		node_ids = SyncUserVehicleNodes._collect_node_ids(spec)

		assert swap_transmission.id in node_ids
		assert trim_transmission.id not in node_ids

	def test_no_body_when_trim_body_is_none(self) -> None:
		engine = _make_engine()
		transmission = _make_transmission()
		spec = _make_spec(
			trim_engine=engine,
			trim_transmission=transmission,
			trim_body_id=None,
		)

		node_ids = SyncUserVehicleNodes._collect_node_ids(spec)

		assert node_ids == {engine.id, transmission.id}

	def test_missing_aggregates_yield_empty(self) -> None:
		spec = _make_spec(trim_engine=None, trim_transmission=None, trim_body_id=None)

		node_ids = SyncUserVehicleNodes._collect_node_ids(spec)

		assert node_ids == set()


class TestForUserVehicle:
	"""Поведение ``for_user_vehicle`` при отсутствии спецификации."""

	def test_returns_empty_when_no_spec(self) -> None:
		fake_session = MagicMock()
		fake_session.commit = AsyncMock()

		class _SessionCM:
			async def __aenter__(self) -> Any:
				return fake_session

			async def __aexit__(self, *args: Any) -> None:
				return None

		with (
			patch(
				'apps.vehicles.services.sync_user_vehicle_nodes.database.get_async_session',
				return_value=_SessionCM(),
			),
			patch.object(SyncUserVehicleNodes, '_load_spec', new=AsyncMock(return_value=None)),
		):
			result = _run(SyncUserVehicleNodes.for_user_vehicle(uuid4()))

		assert result == []
		fake_session.commit.assert_not_awaited()
