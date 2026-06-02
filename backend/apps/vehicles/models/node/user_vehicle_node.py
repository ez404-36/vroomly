from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import UUID, Column, ForeignKey, String, Table, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.vehicles.models.node.vehicle_node import get_vehicle_node_link_mixin
from apps.vehicles.models.vehicle.user_vehicle import get_user_vehicle_link_mixin
from common.models.fields.foreign_key_to import PostgresOnDeleteFK
from common.models.mixins.relations import get_foreign_key_mixin
from core.models import AutoSchemaBase

if TYPE_CHECKING:
	from apps.vehicles.models.vehicle.reminder import VehicleReminder


reminder_node_link = Table(
	'reminder_node_link',
	AutoSchemaBase.metadata,
	Column(
		'reminder_id',
		UUID,
		ForeignKey('vehicles.vehicle_reminder.id', ondelete='CASCADE'),
		primary_key=True,
	),
	Column(
		'user_vehicle_node_id',
		UUID,
		ForeignKey('vehicles.user_vehicle_node.id', ondelete='CASCADE'),
		primary_key=True,
	),
	schema='vehicles',
)


class UserVehicleNode(
	AutoSchemaBase,
	get_user_vehicle_link_mixin(back_populates='nodes', nullable=False),
	get_vehicle_node_link_mixin(back_populates='user_vehicle_nodes', nullable=False, on_delete='RESTRICT'),
):
	"""
	Экземпляр узла/агрегата на конкретной машине пользователя.

	Связывает запись гаража (``UserVehicle``) со справочным узлом
	(``VehicleNode``: двигатель, КПП, кузов и т. д.). Служит якорем для
	пер-машинных событий — напоминаний (M:N через ``reminder_node_link``)
	и будущей истории обслуживания.

	Пер-агрегатные данные минимальны: только ``notes``. «Последнее
	обслуживание» и т. п. будут производными от ``ServiceHistory``.
	"""

	notes: Mapped[str | None] = mapped_column(String(255), doc='Заметка по узлу на этой машине')

	reminders: Mapped[list[VehicleReminder]] = relationship(
		'VehicleReminder',
		secondary=reminder_node_link,
		back_populates='nodes',
		lazy='select',
	)

	__table_args__ = (
		UniqueConstraint(
			'user_vehicle_id',
			'vehicle_node_id',
			name='user_vehicle_node_unique',
		),
	)


def get_user_vehicle_node_link_mixin(
	back_populates: str | None,
	nullable: bool,
	verbose_name: str = 'Узел ТС пользователя',
	on_delete: PostgresOnDeleteFK = 'CASCADE',
):
	"""
	Миксин связи с экземпляром узла ТС пользователя (``UserVehicleNode``).

	Параметр ``on_delete`` обязательно передавать ``'SET NULL'`` для nullable-связей.
	"""
	return get_foreign_key_mixin(
		UserVehicleNode,
		'user_vehicle_node',
		back_populates=back_populates,
		nullable=nullable,
		verbose_name=verbose_name,
		on_delete=on_delete,
	)


# Регистрируем VehicleReminder, чтобы M2M-связь reminders ↔ nodes резолвилась
# при импорте любой из сторон (импорт в конце модуля — после определения
# UserVehicleNode — исключает цикл при загрузке reminder.py).
from apps.vehicles.models.vehicle import reminder as _reminder  # noqa: E402, F401
