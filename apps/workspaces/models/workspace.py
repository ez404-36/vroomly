from pydantic.v1 import UUID4
from sqlalchemy import String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import BaseDBModel
from core.models.mixins.deleted import DeletedModelMixin
from core.models.mixins.timestamped_model import TimestampedModelMixin


class WorkspaceModel(
    BaseDBModel,
    TimestampedModelMixin,
    DeletedModelMixin,
):
    """
    Модель рабочего пространства пользователя.
    Позволяет логически отделять одни привычки от других
    """
    name: Mapped[str] = mapped_column(String(50))
    user_id: Mapped[UUID4] = mapped_column(ForeignKey('users.id'))
    # TODO: settings: Mapped[dict] = mapped_column(BSON, default={})

    __table_args__ = (
        Index('idx_workspace_user_id', 'user_id'),
    )
