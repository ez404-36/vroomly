from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from apps.geo.models.country import get_country_link_mixin
from common.models.fields.foreign_key_to import PostgresOnDeleteFK
from common.models.mixins.code_model import CodeModelMixin, generate_code_on_create
from common.models.mixins.relations import get_foreign_key_mixin
from core.models import AutoSchemaBase


class VehicleConcern(
	AutoSchemaBase,
	CodeModelMixin,
	get_country_link_mixin(back_populates='concerns', nullable=True, on_delete='SET NULL'),
):
	"""
	Концерн/альянс/группа автопроизводителей.
	Примеры: VAG, Hyundai-KIA
	"""

	name: Mapped[str] = mapped_column(String(50), doc='Название концерна на английском языке')
	abbreviation: Mapped[str | None] = mapped_column(String(6), doc='Аббревиатура')


generate_code_on_create(VehicleConcern)


def get_vehicle_concern_link_mixin(
	back_populates: str | None,
	nullable: bool,
	verbose_name: str = 'Концерн',
	on_delete: PostgresOnDeleteFK = 'CASCADE',
):
	"""
	Миксин связи с концерном автопроизводителей.

	Параметр ``on_delete`` обязательно передавать ``'SET NULL'`` для nullable-связей.
	"""
	return get_foreign_key_mixin(
		VehicleConcern,
		'concern',
		back_populates=back_populates,
		nullable=nullable,
		verbose_name=verbose_name,
		on_delete=on_delete,
	)
