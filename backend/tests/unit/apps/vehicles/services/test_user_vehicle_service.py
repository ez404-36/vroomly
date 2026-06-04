"""Tests for UserVehicleService — бизнес-логика создания ТС и обновления пробега."""

import asyncio
from typing import Any, Coroutine, TypeVar
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from apps.vehicles.api.user_vehicle.schemas import CreateUserVehicleSchema, UpdateMileageSchema
from apps.vehicles.services.user_vehicle import UserVehicleService

T = TypeVar('T')


def _run(coro: Coroutine[Any, Any, T]) -> T:
	"""Запускает корутину в свежем event loop."""
	return asyncio.run(coro)


def _make_session_cm(session: Any) -> Any:
	"""Создаёт async-context-manager, отдающий ``session``."""
	cm = MagicMock()
	cm.__aenter__ = AsyncMock(return_value=session)
	cm.__aexit__ = AsyncMock(return_value=False)
	return cm


def _make_session() -> Any:
	session = MagicMock()
	session.add = MagicMock()
	session.flush = AsyncMock()
	session.commit = AsyncMock()
	return session


class TestUserVehicleServiceUpdateMileage:
	"""update_mileage: проверки владения и обновления пробега на Vehicle."""

	def test_returns_none_when_not_owned(self):
		"""Если ТС не принадлежит пользователю — возвращается None (без коммита)."""
		session = _make_session()
		user_id = uuid4()
		uv_id = uuid4()

		repo = MagicMock()
		repo.get_owned_with_chain = AsyncMock(return_value=None)

		with (
			patch(
				'apps.vehicles.services.user_vehicle.database.get_async_session',
				return_value=_make_session_cm(session),
			),
			patch(
				'apps.vehicles.services.user_vehicle.UserVehicleRepository',
				return_value=repo,
			),
		):
			result = _run(
				UserVehicleService().update_mileage(uv_id, user_id, UpdateMileageSchema(mileage=100)),
			)

		assert result is None
		session.commit.assert_not_called()

	def test_returns_none_when_vehicle_missing(self):
		"""ТС найдено, но без связанного Vehicle — None, без коммита."""
		session = _make_session()
		user_vehicle = MagicMock(vehicle=None)

		repo = MagicMock()
		repo.get_owned_with_chain = AsyncMock(return_value=user_vehicle)

		with (
			patch(
				'apps.vehicles.services.user_vehicle.database.get_async_session',
				return_value=_make_session_cm(session),
			),
			patch(
				'apps.vehicles.services.user_vehicle.UserVehicleRepository',
				return_value=repo,
			),
		):
			result = _run(
				UserVehicleService().update_mileage(uuid4(), uuid4(), UpdateMileageSchema(mileage=100)),
			)

		assert result is None
		session.commit.assert_not_called()

	def test_updates_vehicle_mileage_and_commits(self):
		"""Успех: пробег пишется на Vehicle, транзакция коммитится, возвращается перечитанный ТС."""
		session = _make_session()
		vehicle = MagicMock(mileage=0, is_mileage_in_miles=False)
		user_vehicle = MagicMock(id=uuid4(), vehicle=vehicle)
		reloaded = MagicMock()

		repo = MagicMock()
		repo.get_owned_with_chain = AsyncMock(return_value=user_vehicle)
		repo.get_with_chain = AsyncMock(return_value=reloaded)

		with (
			patch(
				'apps.vehicles.services.user_vehicle.database.get_async_session',
				return_value=_make_session_cm(session),
			),
			patch(
				'apps.vehicles.services.user_vehicle.UserVehicleRepository',
				return_value=repo,
			),
		):
			result = _run(
				UserVehicleService().update_mileage(
					uuid4(),
					uuid4(),
					UpdateMileageSchema(mileage=54321, is_mileage_in_miles=True),
				),
			)

		assert result is reloaded
		assert vehicle.mileage == 54321
		assert vehicle.is_mileage_in_miles is True
		session.commit.assert_awaited_once()


class TestUserVehicleServiceCreate:
	"""create: транзакционное создание Vehicle (+CarSpec) + UserVehicle."""

	def test_creates_without_spec_when_no_trim_or_vin(self):
		"""Без trim_id/vin CarSpec не создаётся — добавляются только Vehicle и UserVehicle."""
		session = _make_session()
		created = MagicMock()

		repo = MagicMock()
		repo.get_with_chain = AsyncMock(return_value=created)

		with (
			patch(
				'apps.vehicles.services.user_vehicle.database.get_async_session',
				return_value=_make_session_cm(session),
			),
			patch(
				'apps.vehicles.services.user_vehicle.UserVehicleRepository',
				return_value=repo,
			),
		):
			result = _run(
				UserVehicleService().create(CreateUserVehicleSchema(production_year=2020), uuid4()),
			)

		assert result is created
		# Vehicle + UserVehicle = 2 add-вызова (без CarSpec)
		assert session.add.call_count == 2
		session.commit.assert_awaited_once()

	def test_creates_spec_when_trim_and_vin_present(self):
		"""С trim_id и vin создаётся CarSpec — 3 add-вызова."""
		session = _make_session()
		repo = MagicMock()
		repo.get_with_chain = AsyncMock(return_value=MagicMock())

		data = CreateUserVehicleSchema(
			production_year=2020,
			trim_id=str(uuid4()),
			vin='1HGBH41JXMN109186',
		)

		with (
			patch(
				'apps.vehicles.services.user_vehicle.database.get_async_session',
				return_value=_make_session_cm(session),
			),
			patch(
				'apps.vehicles.services.user_vehicle.UserVehicleRepository',
				return_value=repo,
			),
		):
			_run(UserVehicleService().create(data, uuid4()))

		# Vehicle + CarSpec + UserVehicle = 3 add-вызова
		assert session.add.call_count == 3
		session.commit.assert_awaited_once()
