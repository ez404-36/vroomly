from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from apps.accounts.models.user import get_user_link_mixin
from core.models import AutoSchemaBase


class VehicleGroup(
    AutoSchemaBase,
    get_user_link_mixin('groups', False),
):
    """
    Модель Группа ТС
    """

    name: Mapped[str] = mapped_column(String(50), doc='Название группы')
    notes: Mapped[str | None] = mapped_column(String(255), doc='Заметки/Описание группы')
