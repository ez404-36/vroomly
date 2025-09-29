from sqlalchemy import SmallInteger
from sqlalchemy.orm import mapped_column, Mapped

from apps.vehicles.models.motorcycle.enums import MotorcycleBodyType
from apps.vehicles.models.vehicle.abstract.vehicle_body import VehicleBodyAbstract
from common.models import IntEnumType
from core.models import AutoSchemaBase


class MotorcycleBody(
    VehicleBodyAbstract,
    AutoSchemaBase,
):
    """
    Спецификация кузова мотоцикла
    """

    type: Mapped[MotorcycleBodyType] = mapped_column(
        IntEnumType(MotorcycleBodyType), doc='Тип кузова'
    )
    seat_height: Mapped[int | None] = mapped_column(SmallInteger, doc='Высота сиденья')
