from typing import Any

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from core.models import AutoSchemaBase


class VehicleTrimAbstract(
	AutoSchemaBase,
):
	"""
	Базовый класс комплектации ТС.

	Связь с двигателем (engine_id) выносится в конкретные подклассы
	(CarTrim, MotorcycleTrim), чтобы backref-имена не пересекались
	на одной таблице VehicleEngine.
	"""

	__abstract__ = True

	name: Mapped[str] = mapped_column(String(50), doc='Название комплектации')
	options: Mapped[dict[str, Any] | None] = mapped_column(JSONB, default={})
