"""replace trigram GIN indexes with case-insensitive lower(name) variant

Revision ID: b2c3d4e5f6a7
Revises: a1f2b3c4d5e6
Create Date: 2026-05-28 15:30:00.000000

``pg_trgm`` функция ``similarity`` регистрозависима: триграммы извлекаются
из исходной строки как есть. Сервис ``GuessCommonCarInfo`` сравнивает
переведённое название ("TUXON", "TUCSON") с записями в БД, которые
хранятся в произвольном регистре ("Tucson"). Без приведения регистра
score падает почти до нуля.

Поэтому индексы пересоздаются на ``lower(name)``, а сервис использует
``func.lower(...)`` с обеих сторон сравнения.
"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1f2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('DROP INDEX IF EXISTS vehicles.ix_vehicle_brand_name_trgm')
    op.execute('DROP INDEX IF EXISTS vehicles.ix_vehicle_series_name_trgm')
    op.execute(
        'CREATE INDEX IF NOT EXISTS ix_vehicle_brand_name_lower_trgm '
        'ON vehicles.vehicle_brand USING gin (lower(name) gin_trgm_ops)'
    )
    op.execute(
        'CREATE INDEX IF NOT EXISTS ix_vehicle_series_name_lower_trgm '
        'ON vehicles.vehicle_series USING gin (lower(name) gin_trgm_ops)'
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('DROP INDEX IF EXISTS vehicles.ix_vehicle_series_name_lower_trgm')
    op.execute('DROP INDEX IF EXISTS vehicles.ix_vehicle_brand_name_lower_trgm')
    op.execute(
        'CREATE INDEX IF NOT EXISTS ix_vehicle_brand_name_trgm '
        'ON vehicles.vehicle_brand USING gin (name gin_trgm_ops)'
    )
    op.execute(
        'CREATE INDEX IF NOT EXISTS ix_vehicle_series_name_trgm '
        'ON vehicles.vehicle_series USING gin (name gin_trgm_ops)'
    )
