"""vehicle_engine natural key unique indexes

Revision ID: d4e7a2c81b6f
Revises: c1a3f9e7b5d2
Create Date: 2026-05-28 12:15:00.000000

Добавление частичных уникальных индексов на естественный ключ двигателя:
- (brand_id, name, volume, power) WHERE brand_id IS NOT NULL
- (concern_id, name, volume, power) WHERE concern_id IS NOT NULL

Один из brand_id / concern_id всегда NOT NULL (гарантируется CHECK
``vehicle_engine_brand_or_concern_required``), поэтому два частичных
индекса полностью покрывают пространство строк.

Поля volume и power добавлены к (brand_id|concern_id, name), потому что
"name" двигателя обозначает семейство, а конкретная спецификация
определяется как минимум объёмом и мощностью.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e7a2c81b6f'
down_revision: Union[str, None] = 'c1a3f9e7b5d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        'vehicle_engine_brand_name_volume_power_unique',
        'vehicle_engine',
        ['brand_id', 'name', 'volume', 'power'],
        unique=True,
        schema='vehicles',
        postgresql_where=sa.text('brand_id IS NOT NULL'),
    )
    op.create_index(
        'vehicle_engine_concern_name_volume_power_unique',
        'vehicle_engine',
        ['concern_id', 'name', 'volume', 'power'],
        unique=True,
        schema='vehicles',
        postgresql_where=sa.text('concern_id IS NOT NULL'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        'vehicle_engine_concern_name_volume_power_unique',
        table_name='vehicle_engine',
        schema='vehicles',
        postgresql_where=sa.text('concern_id IS NOT NULL'),
    )
    op.drop_index(
        'vehicle_engine_brand_name_volume_power_unique',
        table_name='vehicle_engine',
        schema='vehicles',
        postgresql_where=sa.text('brand_id IS NOT NULL'),
    )
