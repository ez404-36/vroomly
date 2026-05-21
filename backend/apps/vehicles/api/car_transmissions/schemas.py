from fastapi_utils.api_model import APIModel
from pydantic import Field


class TransmissionSchema(APIModel):
	"""Схема трансмиссии."""

	id: str = Field(description='ID трансмиссии')
	name: str = Field(description='Название')
	index: str | None = Field(default=None, description='Заводской индекс')
	type: str = Field(description='Тип коробки передач')
	gears: int = Field(description='Количество передач')
	drive_types: list[str] = Field(default_factory=list, description='Типы привода')
	torque: int | None = Field(default=None, description='Крутящий момент (Нм)')
