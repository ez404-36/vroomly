from sqlalchemy import SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.car.enums import CarBodyType
from apps.vehicles.models.vehicle.abstract.vehicle_body import VehicleBodyAbstract
from common.models import IntEnumType
from core.models import AutoSchemaBase


class CarBody(
    VehicleBodyAbstract,
    AutoSchemaBase,
):
    """
    Кузов автомобиля
    """

    type: Mapped[CarBodyType] = mapped_column(
        IntEnumType(CarBodyType), doc='Тип кузова'
    )
    trunk_volume: Mapped[int | None] = mapped_column(SmallInteger, doc='Объем багажника')
