from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.vehicle.enums import VehicleBodyType
from common.models import IntFlagType
from core.models import AutoSchemaBase


class VehicleBodyAbstract(
    AutoSchemaBase,
):
    """
    Базовый класс кузова ТС
    """
    __abstract__ = True

    name: Mapped[str | None] = mapped_column(String(50), doc='Название кузова')
    material: Mapped[VehicleBodyType | None] = mapped_column(
        IntFlagType(VehicleBodyType),
        doc='Основной материал кузова (комбинация флагов VehicleBodyType)',
    )
