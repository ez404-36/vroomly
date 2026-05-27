from uuid import UUID

from fastapi_utils.api_model import APIModel
from pydantic import Field


class VehicleTrimListSchema(APIModel):
    id: UUID
    name: str
    generation_id: UUID


class TrimSchema(APIModel):
    """Схема комплектации."""

    id: str = Field(description='ID комплектации')
    name: str = Field(description='Название комплектации')
    avg_fuel_consumption: float | None = Field(default=None, description='Средний расход топлива (по паспорту)')
    acceleration: float | None = Field(default=None, description='Разгон до 100 км/ч (по паспорту)')
    clearance: int | None = Field(default=None, description='Клиренс')
