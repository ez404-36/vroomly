from sqlalchemy import String, UniqueConstraint, event
from sqlalchemy.orm import Mapped, mapped_column

from apps.geo.models.country import get_country_link_mixin
from apps.vehicles.models.vehicle.vehicle_concern import get_vehicle_concern_link_mixin
from common.models.mixins.relations import get_foreign_key_mixin
from common.utils.generators import generate_code
from core.models import AutoSchemaBase


class VehicleBrand(
    AutoSchemaBase,
    get_country_link_mixin(back_populates='brands', nullable=False),
    get_vehicle_concern_link_mixin(back_populates='brands', nullable=True),
):
    """
    Марка ТС (Торговая).
    Примеры: Skoda, BMW, Lada
    """

    code: Mapped[str] = mapped_column(
        String(50), doc='КОД_БРЕНДА (англ. язык, верхний регистр)'
    )
    name: Mapped[str] = mapped_column(
        String(50), doc='Название бренда на английском языке'
    )
    abbreviation: Mapped[str | None] = mapped_column(
        String(6), doc='Аббревиатура'
    )
    original_name: Mapped[str | None] = mapped_column(
        String(50), doc='Название бренда на родном языке, если отличается от name'
    )

    __table_args__ = (
        UniqueConstraint(
            'country_id', 'code', name='vehicle_brand_country_id_code_unique'
        ),
    )


def get_vehicle_brand_link_mixin(
    back_populates: str | None,
    nullable: bool,
    verbose_name='Марка',
):
    """
    Миксин связи со страной
    """
    return get_foreign_key_mixin(
        VehicleBrand, 'brand',
        back_populates=back_populates, nullable=nullable, verbose_name=verbose_name
    )


@event.listens_for(VehicleBrand, 'before_insert')
def __generate_code_listener(mapper, connection, target):
    """Генерация кода марки ТС по аббревиатуре или названию марки"""
    if not target.code:
        target.code = generate_code(target.abbreviation or target.name)
