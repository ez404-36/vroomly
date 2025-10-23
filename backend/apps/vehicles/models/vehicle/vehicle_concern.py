from sqlalchemy import String, event
from sqlalchemy.orm import Mapped, mapped_column

from apps.geo.models.country import get_country_link_mixin
from common.models.mixins.relations import get_foreign_key_mixin
from common.utils.generators import generate_code
from core.models import AutoSchemaBase



class VehicleConcern(
    AutoSchemaBase,
	get_country_link_mixin(back_populates='concerns', nullable=True),
):
    """
    Концерн/альянс/группа автопроизводителей.
    Примеры: VAG, Hyundai-KIA
    """

    code: Mapped[str] = mapped_column(
        String(50), doc='КОД_КОНЦЕРНА (англ. язык, верхний регистр)'
    )
    name: Mapped[str] = mapped_column(
        String(50), doc='Название концерна на английском языке'
    )
    abbreviation: Mapped[str | None] = mapped_column(
        String(6), doc='Аббревиатура'
    )


@event.listens_for(VehicleConcern, 'before_insert')
def __generate_code_and_abbreviation_listener(mapper, connection, target):
    """Генерация кода и аббревиатуры концерна по его названию"""
    if target.name and not target.code:
        target.code = generate_code(target.name)


def get_vehicle_concern_link_mixin(
    back_populates: str | None,
    nullable: bool,
    verbose_name='Концерн',
):
    """
    Миксин связи с концерном автопроизводителей
    """
    return get_foreign_key_mixin(
        VehicleConcern, 'concern',
        back_populates=back_populates, nullable=nullable, verbose_name=verbose_name
    )
