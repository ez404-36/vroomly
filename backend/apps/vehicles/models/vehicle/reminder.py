from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.accounts.models.user import get_user_link_mixin
from apps.vehicles.models.vehicle.user_vehicle import get_user_vehicle_link_mixin
from common.models import TimestampedModelMixin
from core.models import AutoSchemaBase

if TYPE_CHECKING:
	from apps.vehicles.models.node.user_vehicle_node import UserVehicleNode


class VehicleReminder(
	AutoSchemaBase,
	TimestampedModelMixin,
	get_user_link_mixin('reminders', False),
	get_user_vehicle_link_mixin(back_populates='reminders', nullable=False),
):
	"""
	Напоминание по ТС в гараже пользователя.

	Привязано к ``UserVehicle`` (удаляется вместе с ТС). Хранит суть
	напоминания, опциональные дату/время выполнения и статус выполнения.
	Выполненные напоминания остаются в таблице (``is_completed`` +
	``completed_at``) и формируют историю.

	Может быть связано с несколькими узлами ТС (``UserVehicleNode``) через
	M:N ``reminder_node_link`` — например, «всё, что связано с двигателем».
	"""

	title: Mapped[str] = mapped_column(String(100), doc='Суть напоминания')
	description: Mapped[str | None] = mapped_column(String(500), nullable=True, doc='Детали напоминания')
	due_at: Mapped[datetime | None] = mapped_column(
		DateTime(timezone=True),
		nullable=True,
		doc='Дата/время выполнения',
	)
	is_all_day: Mapped[bool] = mapped_column(
		Boolean,
		default=False,
		doc='Напоминание на весь день (без времени) ?',
	)
	is_completed: Mapped[bool] = mapped_column(
		Boolean,
		default=False,
		doc='Напоминание выполнено ?',
	)
	completed_at: Mapped[datetime | None] = mapped_column(
		DateTime(timezone=True),
		nullable=True,
		doc='Дата/время отметки о выполнении',
	)

	nodes: Mapped[list[UserVehicleNode]] = relationship(
		'UserVehicleNode',
		secondary='vehicles.reminder_node_link',
		back_populates='reminders',
		lazy='select',
	)
