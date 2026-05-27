from uuid import UUID

from pydantic import BaseModel, Field


class VehicleSeriesFilterParams(BaseModel):
	brand: UUID = Field(description='ID бренда')
	search: str = Field(description='Поиск по названию модели', default=None)
