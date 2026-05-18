from uuid import UUID

from fastapi_utils.api_model import APIModel


class VehicleGenerationListSchema(APIModel):
    id: UUID
    name: str
    series_id: UUID
    start_year: int
    end_year: int | None