from typing import Literal

from pydantic import BaseModel, Field


class VehicleBrandFilterParams(BaseModel):
    ordering: Literal["country_id", "code"] = Field(
        description="Сортировка", default="code"
    )
    search: str = Field(description="Поиск (по названию/коду)", default=None)
    country: str = Field(description="Фильтрация по коду страны", default=None)
