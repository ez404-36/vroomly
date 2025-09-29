from apps.vehicles.models.utils import SpecBackRefs
from apps.vehicles.models.vehicle.vehicle import get_vehicle_link_mixin
from apps.vehicles.models.vehicle.vehicle_generation import get_vehicle_generation_link_mixin
from core.models import AutoSchemaBase


class MotorcycleSpec(
    AutoSchemaBase,
    get_vehicle_link_mixin(SpecBackRefs.MOTORCYCLE, False),
    get_vehicle_generation_link_mixin(None, False),
):
    """
    Спецификация мотоцикла
    """
