from sqlalchemy import SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.motorcycle.enums import MotorcycleCoolingType
from apps.vehicles.models.utils import SpecBackRefs
from apps.vehicles.models.vehicle.vehicle_engine import get_engine_link_mixin
from common.models import IntEnumType
from core.models import AutoSchemaBase


class MotorcycleEngineSpec(
    AutoSchemaBase,
    get_engine_link_mixin(SpecBackRefs.MOTORCYCLE, False),
):
    """
    Спецификация для двигателя мотоцикла
    """

    cooling: Mapped[MotorcycleCoolingType] = mapped_column(
        IntEnumType(MotorcycleCoolingType), doc='Тип охлаждения'
    )
    stroke: Mapped[int] = mapped_column(SmallInteger, doc='Число тактов')
    cylinders: Mapped[int] = mapped_column(SmallInteger, doc='Кол-во цилиндров')
