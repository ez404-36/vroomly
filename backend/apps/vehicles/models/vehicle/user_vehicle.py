from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.accounts.models.user import get_user_link_mixin
from apps.vehicles.models.vehicle.vehicle import get_vehicle_link_mixin
from apps.vehicles.models.vehicle.vehicle_group import user_vehicle_group_link
from core.models import AutoSchemaBase

if TYPE_CHECKING:
    from apps.vehicles.models.vehicle.vehicle_group import VehicleGroup


class UserVehicle(
    AutoSchemaBase,
    get_user_link_mixin('vehicles', False),
    get_vehicle_link_mixin('user_vehicles', False),
):
    """
    ТС, добавленное в гараж пользователя.

    Содержит только данные, специфичные для конкретного владения
    (средний расход у этого пользователя, заметки, фото).
    Пробег и единицы измерения — атрибуты самого ``Vehicle`` (заводская
    модель ТС, не зависит от пользователя): см. ``Vehicle.mileage``,
    ``Vehicle.is_mileage_in_miles``.
    """
    avg_fuel_consumption: Mapped[Decimal | None] = mapped_column(
        Numeric(4, 2, asdecimal=True),
        doc='Средний расход топлива (у этого пользователя)',
    )
    # TODO photo_id

    groups: Mapped[list[VehicleGroup]] = relationship(
        'VehicleGroup',
        secondary=user_vehicle_group_link,
        back_populates='user_vehicles',
        lazy='select',
    )
