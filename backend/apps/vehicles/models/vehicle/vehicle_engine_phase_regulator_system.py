from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from apps.vehicles.models.vehicle.enums import VehicleEnginePhaseRegulatorType
from apps.vehicles.models.vehicle.vehicle_brand import get_vehicle_brand_link_mixin
from apps.vehicles.models.vehicle.vehicle_concern import get_vehicle_concern_link_mixin
from common.models import IntEnumType
from common.models.mixins.code_model import CodeModelMixin, generate_code_on_create
from common.models.mixins.relations import get_foreign_key_mixin
from core.models import AutoSchemaBase


class VehicleEnginePhaseRegulatorSystem(
    AutoSchemaBase,
    CodeModelMixin,
    get_vehicle_brand_link_mixin(back_populates='phase_regulator_systems', nullable=True),
    get_vehicle_concern_link_mixin(back_populates='phase_regulator_systems', nullable=True),
):
    """
    Система управления фазами газораспределением в двигателе (Фазорегулятор)
    """

    name: Mapped[str] = mapped_column(
        String(50), doc='Название'
    )
    phase_regulator_type: Mapped[VehicleEnginePhaseRegulatorType | None] = mapped_column(
        IntEnumType(VehicleEnginePhaseRegulatorType), doc='Фазорегулятор'
    )


generate_code_on_create(VehicleEnginePhaseRegulatorSystem)


def get_phase_regulator_system_mixin(
    back_populates: str | None,
    nullable: bool,
    verbose_name='Система фазорегулирования',
):
    """
    Миксин связи с системой фазорегулирования двигателя
    """
    return get_foreign_key_mixin(
        VehicleEnginePhaseRegulatorSystem, 'phase_regulator_system',
        back_populates=back_populates, nullable=nullable, verbose_name=verbose_name,
    )
