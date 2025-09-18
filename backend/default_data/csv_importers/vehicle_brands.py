from apps.vehicles.models.vehicle_brand import VehicleBrand, generate_brand_code

from .base import ImportFromCSVBase


class ImportVehicleBrandsCSV(ImportFromCSVBase):
    model = VehicleBrand
    filename = "vehicle_brand.csv"
    mapper = {
        "country": "country_id",
    }

    def transform_data(self, instance_data: dict) -> dict:
        if "code" not in instance_data:
            instance_data["code"] = generate_brand_code(instance_data.get("name"))

        return instance_data
