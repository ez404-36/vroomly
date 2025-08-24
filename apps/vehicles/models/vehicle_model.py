from enum import IntEnum

from pydantic.v1 import UUID4
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.vehicle_brand import VehicleBrand
from core.models import AutoSchemaBase
from common.models import IntEnumType, ForeignKeyTo


class VehicleType(IntEnum):
    """Тип ТС"""
    CAR = 0
    MOTORCYCLE = 1



class VehicleModel(
    AutoSchemaBase,
):
    """
    Модель "Модель ТС". Является родительской сущностью для Car, Motorcycle.
    Примеры: Octavia (Skoda), Vesta (Lada)
    """
    
    brand_id: Mapped[UUID4] = mapped_column(ForeignKeyTo(VehicleBrand))
    name: Mapped[str] = mapped_column(String(50))
    vehicle_type: Mapped[VehicleType] = mapped_column(IntEnumType(VehicleType))
