from apps.accounts.models.user import User
from common.models import ForeignKeyTo
from core.models import AutoSchemaBase
from pydantic.v1 import UUID4
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class VehicleGroup(
    AutoSchemaBase,
):
    """
    Модель Группа ТС
    """

    user_id: Mapped[UUID4] = mapped_column(ForeignKeyTo(User))
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str | None]
