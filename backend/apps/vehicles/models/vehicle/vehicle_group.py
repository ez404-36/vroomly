from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import UUID, Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.accounts.models.user import get_user_link_mixin
from core.models import AutoSchemaBase

if TYPE_CHECKING:
	from apps.vehicles.models.vehicle.user_vehicle import UserVehicle


user_vehicle_group_link = Table(
	'user_vehicle_group_link',
	AutoSchemaBase.metadata,
	Column('user_vehicle_id', UUID, ForeignKey('vehicles.user_vehicle.id', ondelete='CASCADE'), primary_key=True),
	Column('group_id', UUID, ForeignKey('vehicles.vehicle_group.id', ondelete='CASCADE'), primary_key=True),
	schema='vehicles',
)


class VehicleGroup(
	AutoSchemaBase,
	get_user_link_mixin('groups', False),
):
	"""
	Группа ТС в гараже пользователя.

	Одно ТС может принадлежать нескольким группам (M:N через
	``user_vehicle_group_link``).
	"""

	name: Mapped[str] = mapped_column(String(50), doc='Название группы')
	notes: Mapped[str | None] = mapped_column(String(255), doc='Заметки/Описание группы')

	user_vehicles: Mapped[list['UserVehicle']] = relationship(
		'UserVehicle',
		secondary=user_vehicle_group_link,
		back_populates='groups',
		lazy='select',
	)
