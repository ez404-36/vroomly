from datetime import date

from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column

from apps.geo.models.country import get_country_link_mixin
from common.models import DeletedModelMixin, TimestampedModelMixin
from common.models.mixins.relations import get_foreign_key_mixin
from core.models import AutoSchemaBase


class User(
	AutoSchemaBase,
	DeletedModelMixin,
	TimestampedModelMixin,
	get_country_link_mixin(
		back_populates='users',
		nullable=True,
		verbose_name='Местоположение (страна)',
		on_delete='SET NULL',
	),
):
	"""
	Пользователь
	"""

	login: Mapped[str] = mapped_column(String(50), unique=True)
	email: Mapped[str] = mapped_column(String(50), unique=True)
	password_hash: Mapped[str] = mapped_column(String(255))

	name: Mapped[str | None]
	surname: Mapped[str | None]
	birth_date: Mapped[date | None] = mapped_column(Date)


def get_user_link_mixin(
	back_populates: str | None,
	nullable: bool,
	verbose_name='Пользователь',
):
	"""
	Миксин связи с пользователем
	"""
	return get_foreign_key_mixin(
		User,
		'user',
		back_populates=back_populates,
		nullable=nullable,
		verbose_name=verbose_name,
	)
