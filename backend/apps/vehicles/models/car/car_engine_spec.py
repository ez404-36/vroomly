from sqlalchemy import String, SmallInteger, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.utils import SpecBackRefs
from apps.vehicles.models.vehicle.vehicle_engine import get_engine_link_mixin
from core.models import AutoSchemaBase


class CarEngineSpec(
	AutoSchemaBase,
	get_engine_link_mixin(SpecBackRefs.CAR, False),
):
	"""
	Спецификация для двигателя автомобиля
	"""

	eco_class: Mapped[str] = mapped_column(String(50), doc='Экологический класс')
	cylinders: Mapped[int] = mapped_column(SmallInteger, doc='Кол-во цилиндров')
	is_turbo: Mapped[bool] = mapped_column(Boolean, doc='Турбированный')
