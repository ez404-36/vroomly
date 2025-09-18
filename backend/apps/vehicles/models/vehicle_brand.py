from apps.geo.models.country import Country
from common.models import ForeignKeyTo
from core.models import AutoSchemaBase
from sqlalchemy import String, UniqueConstraint, event
from sqlalchemy.orm import Mapped, mapped_column


def generate_brand_code(brand_name: str) -> str:
    return (
        brand_name.upper()
        .replace(" ", "_")
        .replace(".", "")
        .replace("&", "AND")
        .replace("(", "")
        .replace(")", "")
    )


class VehicleBrand(AutoSchemaBase):
    """
    Модель "Марка ТС (Торговая)".
    Примеры: Skoda, BMW, Lada
    """

    country_id: Mapped[str] = mapped_column(ForeignKeyTo(Country))
    code: Mapped[str] = mapped_column(
        String(50)
    )  # КОД_БРЕНДА (англ. язык, верхний регистр)
    name: Mapped[str] = mapped_column(String(50))  # Название бренда на английском языке
    original_name: Mapped[str | None] = mapped_column(
        String(50)
    )  # Название бренда на родном языке, если отличается от name

    __table_args__ = (
        UniqueConstraint(
            "country_id", "code", name="vehicle_brand_country_id_code_unique"
        ),
    )


@event.listens_for(VehicleBrand, "before_insert")
def generate_code_listener(mapper, connection, target):
    # генерация кода марки ТС по названию марки
    if target.name and not target.code:
        target.code = generate_brand_code(target.name)
