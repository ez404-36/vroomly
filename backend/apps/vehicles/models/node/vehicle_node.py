from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from common.models.fields.foreign_key_to import PostgresOnDeleteFK
from common.models.mixins.relations import get_foreign_key_mixin
from core.models import AutoSchemaBase


class VehicleNode(AutoSchemaBase):
	"""
	Базовый узел/агрегат ТС (JTI root).

	Единая адресуемая сущность для основных агрегатов (двигатель, КПП, кузов
	и потенциальные подвеска, тормоза, электрика). Служит точкой привязки для
	экземпляров узлов на машинах пользователей (``UserVehicleNode``) и через
	них — для напоминаний и истории обслуживания.

	Реализована через Joined Table Inheritance: базовая таблица ``vehicle_node``
	хранит идентичность и дискриминатор ``node_type``, а специфичные параметры
	каждого типа узла лежат в отдельных таблицах-деталях (``engine_node``,
	``car_transmission_node`` и т. д.).

	Добавление нового типа узла = новый подкласс с собственным
	``polymorphic_identity`` + Alembic-миграция.

	Базовый узел намеренно НЕ хранит ``name`` и характеристики: ему достаточно
	знать тип агрегата (``node_type``). Название и натуральные ключи уникальности
	(бренд/концерн, объём, мощность и т. д.) живут на таблицах-деталях.
	"""

	node_type: Mapped[str] = mapped_column(String(50), doc='Тип узла (JTI-дискриминатор)')

	__mapper_args__ = {
		'polymorphic_on': node_type,
		'polymorphic_identity': 'node',
	}


def get_vehicle_node_link_mixin(
	back_populates: str | None,
	nullable: bool,
	verbose_name: str = 'Узел ТС',
	on_delete: PostgresOnDeleteFK = 'CASCADE',
	back_uselist: bool = True,
):
	"""
	Миксин связи со справочным узлом ТС (``VehicleNode``).

	Параметр ``on_delete`` обязательно передавать ``'SET NULL'`` для nullable-связей.
	"""
	return get_foreign_key_mixin(
		VehicleNode,
		'vehicle_node',
		back_populates=back_populates,
		nullable=nullable,
		verbose_name=verbose_name,
		on_delete=on_delete,
		back_uselist=back_uselist,
	)
