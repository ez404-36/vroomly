from fastapi_utils.api_model import APIModel
from pydantic import Field


class EngineSchema(APIModel):
	"""Схема двигателя."""

	id: str = Field(description='ID двигателя')
	name: str = Field(description='Название двигателя')
	volume: int = Field(description='Рабочий объём (сс)')
	power: int = Field(description='Мощность (л.с)')
	type: list[str] = Field(default_factory=list, description='Тип двигателя')
	eco_class: str | None = Field(default=None, description='Экологический класс')
	cylinders: int | None = Field(default=None, description='Кол-во цилиндров')
	valves: int | None = Field(default=None, description='Кол-во клапанов')
	torque: int | None = Field(default=None, description='Крутящий момент (Нм)')
	grm_drive_type: str | None = Field(default=None, description='Тип привода ГРМ')
	phase_regulator_type: str | None = Field(default=None, description='Фазорегулятор')
