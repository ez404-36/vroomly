from uuid import UUID

from apps.vehicles.api.vehicle_brand.schemas.readers import VehicleBrandDetailSchema
from fastapi_utils.api_model import APIModel


class VehicleModelListSchema(APIModel):
    id: UUID
    name: str
    brand_id: UUID


class VehicleModelDetailSchema(APIModel):
    id: UUID
    name: str
    brand: VehicleBrandDetailSchema
