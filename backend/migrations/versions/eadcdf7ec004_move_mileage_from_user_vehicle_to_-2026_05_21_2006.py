"""move mileage from user_vehicle to vehicle

Revision ID: eadcdf7ec004
Revises: 957661a10bd9
Create Date: 2026-05-21 20:06:15.780083

Шаг 4 из GRAPH.md: пробег — атрибут самого ТС, а не пользователя.
Поля ``mileage`` и ``is_mileage_in_miles`` переезжают с UserVehicle на Vehicle.

Для ``is_mileage_in_miles`` явно задаём ``server_default='false'``,
чтобы NOT NULL не сломал миграцию на возможных существующих строках.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eadcdf7ec004'
down_revision: Union[str, None] = '957661a10bd9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column('user_vehicle', 'is_mileage_in_miles', schema='vehicles')
    op.drop_column('user_vehicle', 'mileage', schema='vehicles')
    op.add_column(
        'vehicle',
        sa.Column('mileage', sa.Integer(), nullable=True),
        schema='vehicles',
    )
    op.add_column(
        'vehicle',
        sa.Column('is_mileage_in_miles', sa.Boolean(), nullable=False, server_default=sa.false()),
        schema='vehicles',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('vehicle', 'is_mileage_in_miles', schema='vehicles')
    op.drop_column('vehicle', 'mileage', schema='vehicles')
    op.add_column(
        'user_vehicle',
        sa.Column('mileage', sa.INTEGER(), autoincrement=False, nullable=True),
        schema='vehicles',
    )
    op.add_column(
        'user_vehicle',
        sa.Column(
            'is_mileage_in_miles', sa.BOOLEAN(),
            autoincrement=False, nullable=False, server_default=sa.false(),
        ),
        schema='vehicles',
    )
