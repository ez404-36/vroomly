from datetime import date

import bcrypt
from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column

from apps.geo.models.country import get_country_link_mixin
from common.models import DeletedModelMixin, TimestampedModelMixin
from common.models.mixins.relations import get_foreign_key_mixin
from core.models import AutoSchemaBase
from core.settings import settings


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

	@staticmethod
	def generate_password_hash(password: str) -> str:
		salt = bcrypt.gensalt()
		return bcrypt.hashpw(password.encode(settings.encoding), salt).decode(settings.encoding)

	def set_password(self, password: str) -> None:
		"""Генерация пароля"""
		self.password_hash = self.generate_password_hash(password)

	def check_password(self, password: str) -> bool:
		"""Проверка пароля"""
		return bcrypt.checkpw(
			password.encode(settings.encoding),
			self.password_hash.encode(settings.encoding),
		)


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
