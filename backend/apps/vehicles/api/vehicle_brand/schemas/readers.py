from uuid import UUID

from fastapi_utils.api_model import APIModel


class VehicleBrandDetailSchema(APIModel):
	id: UUID
	country_id: str
	code: str
	name: str
	original_name: str | None
