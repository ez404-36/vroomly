import uuid

from pydantic.v1 import UUID4
from sqlalchemy import UUID
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from common.models.fields.foreign_key_to import ForeignKeyTo
from core.models import AutoSchemaBase

VEHICLE_NODE_TABLE = 'vehicles.vehicle_node'


class VehicleNodeDetailMixin:
	"""
	Миксин для таблиц-деталей JTI-иерархии ``VehicleNode``.

	Переопределяет первичный ключ ``id``, делая его одновременно внешним ключом
	на ``vehicle_node.id`` (Joined Table Inheritance). Базовый ``AutoSchemaBase.id``
	объявляет ``id`` как обычный PK с ``default=uuid4``; здесь он становится
	PK + FK на родителя, что и требуется для JTI.

	Подключать в каждый подкласс-деталь ``VehicleNode`` (``EngineNode`` и пр.)
	вместе с ``__mapper_args__ = {'polymorphic_identity': '<type>'}``.
	"""

	@declared_attr
	def id(cls) -> Mapped[UUID4]:  # noqa: N805 — SQLAlchemy declared_attr convention
		return mapped_column(
			UUID,
			ForeignKeyTo(_vehicle_node_model(), on_delete='CASCADE'),
			primary_key=True,
			default=uuid.uuid4,
		)


def _vehicle_node_model() -> type[AutoSchemaBase]:
	"""Ленивый импорт ``VehicleNode`` во избежание циклического импорта."""
	from apps.vehicles.models.node.vehicle_node import VehicleNode

	return VehicleNode
