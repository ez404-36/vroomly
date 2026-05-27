"""drop vehicle_engine name unique indexes

Revision ID: c1a3f9e7b5d2
Revises: 2d0c4b831eae
Create Date: 2026-05-28 12:00:00.000000

Удаление частичных уникальных индексов:
- vehicle_engine_brand_id_name_unique  (brand_id, name) WHERE brand_id IS NOT NULL
- vehicle_engine_concern_id_name_unique (concern_id, name) WHERE concern_id IS NOT NULL

Причина: ограничения семантически некорректны. «Название» двигателя
(например, B16A, M57, Modular, Cyclone) обозначает семейство, а не
отдельную спецификацию. У одного семейства легитимно существуют
несколько модификаций, отличающихся мощностью/крутящим моментом
(например, Honda B16A: 150 л.с./145 Нм и 160 л.с./150 Нм). Это
подтверждается данными в default_data/csv_files/vehicle_engine.csv,
где для сотен (brand_id, name) и (concern_id, name) есть >1 строки
с разными техническими параметрами.

Уникальность спецификации двигателя должна определяться более
широким набором атрибутов (как минимум name + volume + power),
если она вообще необходима.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1a3f9e7b5d2'
down_revision: Union[str, None] = '2d0c4b831eae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_index(
        'vehicle_engine_brand_id_name_unique',
        table_name='vehicle_engine',
        schema='vehicles',
        postgresql_where=sa.text('brand_id IS NOT NULL'),
    )
    op.drop_index(
        'vehicle_engine_concern_id_name_unique',
        table_name='vehicle_engine',
        schema='vehicles',
        postgresql_where=sa.text('concern_id IS NOT NULL'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.create_index(
        'vehicle_engine_concern_id_name_unique',
        'vehicle_engine',
        ['concern_id', 'name'],
        unique=True,
        schema='vehicles',
        postgresql_where=sa.text('concern_id IS NOT NULL'),
    )
    op.create_index(
        'vehicle_engine_brand_id_name_unique',
        'vehicle_engine',
        ['brand_id', 'name'],
        unique=True,
        schema='vehicles',
        postgresql_where=sa.text('brand_id IS NOT NULL'),
    )
