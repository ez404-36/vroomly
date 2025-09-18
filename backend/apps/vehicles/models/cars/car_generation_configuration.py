from decimal import Decimal
from enum import Enum

from apps.vehicles.models.vehicle_engine import VehicleEngine
from apps.vehicles.models.vehicle_generation import VehicleGeneration
from common.models import ForeignKeyTo, IntEnumType
from core.models import AutoSchemaBase
from pydantic.v1 import UUID4
from sqlalchemy import Numeric, SmallInteger, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column


class CarWheelDriveType(Enum):
    """Тип привода"""

    FRONT = 0
    BACK = 1
    FULL = 2


class CarTransmissionType(Enum):
    """Тип коробки передач"""

    MANUAL = 0
    AUTO = 1
    ROBOT = 2
    VARIATOR = 3


class CarBodyType(Enum):
    """Тип кузова"""

    SEDAN = 0
    HATCHBACK = 1
    SW = 2
    COUPE = 3
    CUV = 4
    SUV = 5
    LIFTBACK = 6
    ROADSTER = 7
    VAN = 8
    MINIVAN = 9
    PICKUP_TRUCK = 10
    MINIBUS = 11
    TARGA = 12
    FASTBACK = 13
    LANDAU = 14
    CUV_COUPE = 15
    SHOOTING_BRAKE = 16


class CarGenerationConfiguration(
    AutoSchemaBase,
):
    """
    Модель "Комплектация поколения автомобиля".
    Примеры: Club# (Lada Granta)
    """

    generation_id: Mapped[UUID4] = mapped_column(ForeignKeyTo(VehicleGeneration))
    name: Mapped[str] = mapped_column(String(50))
    transmission: Mapped[CarTransmissionType] = mapped_column(
        IntEnumType(CarTransmissionType)
    )
    body_type: Mapped[CarBodyType] = mapped_column(IntEnumType(CarBodyType))
    engine_id: Mapped[UUID4] = mapped_column(ForeignKeyTo(VehicleEngine))
    wheel_drive: Mapped[CarWheelDriveType] = mapped_column(
        IntEnumType(CarWheelDriveType)
    )

    # region Опциональные параметры

    avg_fuel_consumption: Mapped[Decimal | None] = mapped_column(
        Numeric(3, 2, asdecimal=True)
    )
    acceleration: Mapped[Decimal | None] = mapped_column(Numeric(3, 2, asdecimal=True))
    clearance: Mapped[int | None] = mapped_column(SmallInteger)
    trunk_volume: Mapped[int | None] = mapped_column(SmallInteger)
    options: Mapped[dict | None] = mapped_column(JSONB, default={})

    # end region
