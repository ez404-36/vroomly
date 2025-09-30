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

    material: Mapped[str] = mapped_column(IntFlagType(VehicleBodyType), doc='Основной материал кузова')
