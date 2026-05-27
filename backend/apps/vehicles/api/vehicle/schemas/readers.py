from uuid import UUID

from fastapi_utils.api_model import APIModel

from apps.vehicles.models.vehicle.enums import VehicleType


class VehicleDetailSchema(APIModel):
	id: UUID
	vehicle_type: VehicleType
	production_year: int
	color: str | None
