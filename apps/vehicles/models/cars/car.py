from decimal import Decimal
from enum import Enum

from pydantic.v1 import UUID4
from sqlalchemy import String, Boolean, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from apps.geo.models.country import Country
from apps.vehicles.models.cars.car_generation_configuration import CarGenerationConfiguration
from apps.vehicles.models.vehicle_brand import VehicleBrand
from apps.vehicles.models.vehicle_generation import VehicleGeneration
from apps.vehicles.models.vehicle_model import VehicleModel
from core.models import AutoSchemaBase
from common.models import IntEnumType, ForeignKeyTo


class SteeringWheelPositionType(Enum):
    LEFT = 0
    RIGHT = 1


class Car(
    AutoSchemaBase,
):
    """
    Модель "Автомобиль". Представляет собой добавленный в гараж автомобиль пользователя
    """

    vin: Mapped[str] = mapped_column(String(50))
    body_number: Mapped[str] = mapped_column(String(50))
    number: Mapped[str] = mapped_column(String(15))

    brand_id: Mapped[UUID4] = mapped_column(ForeignKeyTo(VehicleBrand))
    model_id: Mapped[UUID4] = mapped_column(ForeignKeyTo(VehicleModel))
    generation_id: Mapped[UUID4] = mapped_column(ForeignKeyTo(VehicleGeneration))
    configuration_id: Mapped[UUID4] = mapped_column(ForeignKeyTo(CarGenerationConfiguration))
    steering_wheel_position: Mapped[SteeringWheelPositionType] = mapped_column(IntEnumType(SteeringWheelPositionType))

    production_year: Mapped[int | None]
    production_country: Mapped[Country | None] = mapped_column(ForeignKeyTo(Country))
    color: Mapped[str | None] = mapped_column(String(100))
    mileage: Mapped[int | None]
    is_mileage_in_miles: Mapped[bool] = mapped_column(Boolean, default=False)
    avg_fuel_consumption: Mapped[Decimal | None] = mapped_column(Numeric(3, 2, asdecimal=True))

    # TODO photo_id
