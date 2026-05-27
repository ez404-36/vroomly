from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint

from apps.vehicles.models.motorcycle.motorcycle_transmission import get_motorcycle_transmission_link_mixin
from apps.vehicles.models.motorcycle.motorcycle_trim import get_motorcycle_trim_link_mixin
from apps.vehicles.models.utils import SpecBackRefs
from apps.vehicles.models.vehicle.vehicle import get_vehicle_link_mixin
from apps.vehicles.models.vehicle.vehicle_engine import get_engine_link_mixin
from core.models import AutoSchemaBase

if TYPE_CHECKING:
    from apps.vehicles.models.motorcycle.motorcycle_transmission import MotorcycleTransmission
    from apps.vehicles.models.vehicle.vehicle_engine import VehicleEngine


class MotorcycleSpec(
    AutoSchemaBase,
    get_vehicle_link_mixin(SpecBackRefs.MOTORCYCLE, nullable=False, back_uselist=False),
    get_motorcycle_trim_link_mixin('specs', nullable=False),
    get_engine_link_mixin('motorcycle_specs', nullable=True, on_delete='SET NULL'),
    get_motorcycle_transmission_link_mixin('motorcycle_specs', nullable=True, on_delete='SET NULL'),
):
    """
    Спецификация мотоцикла (заводские атрибуты конкретного экземпляра).

    Связи: см. CarSpec — устройство аналогичное. Через ``trim`` доступны
    generation, series, brand, concern. ``engine`` / ``transmission``
    опциональны: NULL ⇒ совпадает с trim, не-NULL ⇒ свап.
    """

    __table_args__ = (
        UniqueConstraint('vehicle_id', name='motorcycle_spec_vehicle_id_unique'),
    )

    @property
    def effective_engine(self) -> 'VehicleEngine':
        """Фактический двигатель экземпляра (свап или из trim)."""
        return self.engine if self.engine_id is not None else self.trim.engine

    @property
    def effective_transmission(self) -> 'MotorcycleTransmission':
        """Фактическая КПП экземпляра (свап или из trim)."""
        return self.transmission if self.transmission_id is not None else self.trim.transmission
