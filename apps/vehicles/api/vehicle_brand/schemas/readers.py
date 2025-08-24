from fastapi_utils.api_model import APIModel


class VehicleBrandDetail(APIModel):
    country_id: str
    code: str
    name: str
    original_name: str | None
