"""enable pg_trgm and add trigram GIN indexes for vehicle_brand and vehicle_series

Revision ID: a1f2b3c4d5e6
Revises: 875066e114c5
Create Date: 2026-05-28 14:00:00.000000

Включение расширения ``pg_trgm`` и создание GIN-индексов с оператором
``gin_trgm_ops`` на ``vehicle_brand.name`` и ``vehicle_series.name``.

Используется сервисом ``GuessCommonCarInfo`` для нечёткого поиска
по результатам перевода названий марок/моделей (libretranslate
ошибается на именах собственных, напр. 'ТУКСОН' -> 'TUXON' вместо
'TUCSON'). Без индексов trigram-сравнение приводит к full scan.

Downgrade удаляет только индексы; расширение ``pg_trgm`` не
сбрасывается, т.к. может использоваться другими частями системы.
"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a1f2b3c4d5e6'
down_revision: Union[str, None] = '875066e114c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm')
    op.execute(
        'CREATE INDEX IF NOT EXISTS ix_vehicle_brand_name_trgm '
        'ON vehicles.vehicle_brand USING gin (name gin_trgm_ops)'
    )
    op.execute(
        'CREATE INDEX IF NOT EXISTS ix_vehicle_series_name_trgm '
        'ON vehicles.vehicle_series USING gin (name gin_trgm_ops)'
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('DROP INDEX IF EXISTS vehicles.ix_vehicle_series_name_trgm')
    op.execute('DROP INDEX IF EXISTS vehicles.ix_vehicle_brand_name_trgm')
