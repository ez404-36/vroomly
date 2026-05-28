"""add vehicle reminder

Revision ID: e057f8de8cb7
Revises: b2c3d4e5f6a7
Create Date: 2026-05-28 21:48:41.058902

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'e057f8de8cb7'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('vehicle_reminder',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=500), nullable=True),
    sa.Column('due_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('is_all_day', sa.Boolean(), nullable=False),
    sa.Column('is_completed', sa.Boolean(), nullable=False),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('user_vehicle_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['accounts.user.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_vehicle_id'], ['vehicles.user_vehicle.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    schema='vehicles'
    )
    op.create_index(
        'ix_vehicle_reminder_user_vehicle_id',
        'vehicle_reminder',
        ['user_vehicle_id'],
        schema='vehicles',
    )
    op.create_index(
        'ix_vehicle_reminder_is_completed',
        'vehicle_reminder',
        ['is_completed'],
        schema='vehicles',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_vehicle_reminder_is_completed', table_name='vehicle_reminder', schema='vehicles')
    op.drop_index('ix_vehicle_reminder_user_vehicle_id', table_name='vehicle_reminder', schema='vehicles')
    op.drop_table('vehicle_reminder', schema='vehicles')
