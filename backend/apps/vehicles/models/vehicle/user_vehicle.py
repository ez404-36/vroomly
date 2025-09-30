from decimal import Decimal

from sqlalchemy import Boolean, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column

from apps.accounts.models.user import get_user_link_mixin
from apps.vehicles.models.vehicle.vehicle import get_vehicle_link_mixin
from core.models import AutoSchemaBase


class UserVehicle(
    AutoSchemaBase,
    get_user_link_mixin('vehicles', False),
    get_vehicle_link_mixin('user_vehicles', False),
):
    """
    ТС, добавленное в гараж пользователя
    """
    mileage: Mapped[int | None] = mapped_column(
        Integer, doc='Пробег',
    )
    is_mileage_in_miles: Mapped[bool] = mapped_column(
        Boolean, default=False, doc='Пробег измеряется в милях ?',
    )
    avg_fuel_consumption: Mapped[Decimal | None] = mapped_column(
        Numeric(3, 2, asdecimal=True),
        doc='Средний расход топлива',
    )
    # TODO photo_id
