from uuid import UUID

from apps.vehicles.api.vehicle_brand.schemas.readers import VehicleBrandDetail
from fastapi_utils.api_model import APIModel


class VehicleModelList(APIModel):
    id: UUID
    name: str
    brand_id: UUID


class VehicleModelDetail(APIModel):
    id: UUID
    name: str
    brand: VehicleBrandDetail
