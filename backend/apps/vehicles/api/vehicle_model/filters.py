from uuid import UUID

from pydantic import BaseModel, Field


class VehicleModelFilterParams(BaseModel):
    brand: UUID = Field(description="ID бренда")
    search: str = Field(description="Поиск по названию модели", default=None)
