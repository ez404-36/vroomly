from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from common.models.fields.foreign_key_to import PostgresOnDeleteFK
from common.models.mixins.relations import get_foreign_key_mixin
from core.models import AutoSchemaBase


class Country(AutoSchemaBase):
    """
    Страна
    """

    id: Mapped[str] = mapped_column(String(3), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    short_name: Mapped[str | None] = mapped_column(
        String(20), unique=True, nullable=True
    )


def get_country_link_mixin(
    back_populates: str | None,
    nullable: bool,
    verbose_name='Страна',
    on_delete: PostgresOnDeleteFK = None,
):
    """
    Миксин связи со страной
    """
    return get_foreign_key_mixin(
        Country, 'country',
        back_populates=back_populates, nullable=nullable,
        verbose_name=verbose_name, on_delete=on_delete,
    )
