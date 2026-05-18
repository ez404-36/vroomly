from uuid import UUID

from fastapi_utils.api_model import APIModel


class VehicleTrimListSchema(APIModel):
    id: UUID
    name: str
    generation_id: UUID