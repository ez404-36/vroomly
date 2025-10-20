from apps.vehicles.models.motorcycle.motorcycle_body import get_motorcycle_body_link_mixin
from apps.vehicles.models.motorcycle.motorcycle_transmission import get_motorcycle_transmission_link_mixin
from apps.vehicles.models.vehicle.abstract.vehicle_trim import VehicleTrimAbstract
from apps.vehicles.models.vehicle.vehicle_generation import get_vehicle_generation_link_mixin


class MotorcycleTrim(
    VehicleTrimAbstract,
    get_vehicle_generation_link_mixin('motorcycle_trims', False),
    get_motorcycle_transmission_link_mixin('motorcycle_trims', False),
    get_motorcycle_body_link_mixin('motorcycle_trims', False),
):
    """
    Комплектация мотоцикла
    """
