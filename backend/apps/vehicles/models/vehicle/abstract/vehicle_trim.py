from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.vehicle.vehicle_engine import get_engine_link_mixin
from core.models import AutoSchemaBase


class VehicleTrimAbstract(
    AutoSchemaBase,
    get_engine_link_mixin('trims', False),
):
    """
    Базовый класс комплектации ТС
    """
    __abstract__ = True

    name: Mapped[str] = mapped_column(String(50), doc='Название комплектации')
    options: Mapped[dict | None] = mapped_column(JSONB, default={})
