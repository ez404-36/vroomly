from uuid import UUID

from fastapi_utils.api_model import APIModel

from apps.vehicles.api.vehicle_brand.schemas.readers import VehicleBrandDetailSchema


class VehicleSeriesListSchema(APIModel):
    id: UUID
    name: str
    brand_id: UUID


class VehicleSeriesDetailSchema(APIModel):
    id: UUID
    name: str
    brand: VehicleBrandDetailSchema
