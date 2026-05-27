"""add car_trim body_str and make body_id nullable

Revision ID: 875066e114c5
Revises: e8b1c47f6a92
Create Date: 2026-05-27 22:05:42.268864

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '875066e114c5'
down_revision: Union[str, None] = 'e8b1c47f6a92'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# FK имя задаём явно: при автогенерации alembic подставлял ``None`` и в
# downgrade у того же имени получалось KeyError. Имя совпадает с тем,
# что было сгенерировано исходной init-миграцией.
_BODY_FK_NAME = 'car_trim_body_id_fkey'


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'car_trim',
        sa.Column('body_str', sa.String(length=50), nullable=True),
        schema='vehicles',
    )
    op.alter_column(
        'car_trim', 'body_id',
        existing_type=sa.UUID(),
        nullable=True,
        schema='vehicles',
    )
    op.drop_constraint(
        _BODY_FK_NAME, 'car_trim',
        schema='vehicles', type_='foreignkey',
    )
    op.create_foreign_key(
        _BODY_FK_NAME, 'car_trim', 'car_body',
        ['body_id'], ['id'],
        source_schema='vehicles', referent_schema='vehicles',
        ondelete='SET NULL',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        _BODY_FK_NAME, 'car_trim',
        schema='vehicles', type_='foreignkey',
    )
    op.create_foreign_key(
        _BODY_FK_NAME, 'car_trim', 'car_body',
        ['body_id'], ['id'],
        source_schema='vehicles', referent_schema='vehicles',
        ondelete='CASCADE',
    )
    op.alter_column(
        'car_trim', 'body_id',
        existing_type=sa.UUID(),
        nullable=False,
        schema='vehicles',
    )
    op.drop_column('car_trim', 'body_str', schema='vehicles')
