from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.utils import SpecBackRefs
from apps.vehicles.models.vehicle.vehicle import get_vehicle_link_mixin
from apps.vehicles.models.vehicle.vehicle_generation import get_vehicle_generation_link_mixin
from core.models import AutoSchemaBase


class CarSpec(
    AutoSchemaBase,
    get_vehicle_link_mixin(SpecBackRefs.CAR, False),
    get_vehicle_generation_link_mixin(None, False),
):
    """
    Спецификация автомобиля
    """

    vin: Mapped[str] = mapped_column(String(17), doc='VIN-номер')
    body_number: Mapped[str | None] = mapped_column(String(50), doc='Номер кузова')
    number: Mapped[str | None] = mapped_column(String(50), doc='Автомобильный номер')
