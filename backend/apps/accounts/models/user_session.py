from datetime import datetime

from sqlalchemy import DateTime, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from apps.accounts.models.user import get_user_link_mixin
from common.models import TimestampedModelMixin
from core.models import AutoSchemaBase


class UserSession(
	AutoSchemaBase,
	TimestampedModelMixin,
	get_user_link_mixin(back_populates=None, nullable=False),
):
	"""
	Сессия пользователя
	"""

	token_jti: Mapped[str] = mapped_column(
		String(255),
		unique=True,
		doc='JWT ID (jti claim)',
	)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default=func.now(),
		doc='Время создания сессии',
	)
	expires_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		doc='Время истечения срока действия токена',
	)

	__table_args__ = (
		Index('ix_user_session_user_id', 'user_id'),
		Index('ix_user_session_token_jti', 'token_jti', unique=True),
	)
