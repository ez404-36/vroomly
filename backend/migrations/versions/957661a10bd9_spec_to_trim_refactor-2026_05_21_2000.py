"""spec to trim refactor

Revision ID: 957661a10bd9
Revises: 5227f16cea20
Create Date: 2026-05-21 20:00:36.747856

Шаг 3 из GRAPH.md:
- Удаляем `generation_id` со Spec (денормализованный дубликат — поколение
  доступно через `spec.trim.generation`).
- Добавляем `trim_id NOT NULL` — каждая Spec обязана ссылаться на Trim.
- Добавляем опциональные `engine_id`, `transmission_id` для отражения
  свапа двигателя / КПП на конкретном экземпляре.

Реальных пользователей в БД нет, data-миграция не требуется.
Таблицы car_spec / motorcycle_spec ожидаются пустыми.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '957661a10bd9'
down_revision: Union[str, None] = '5227f16cea20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # car_spec
    op.add_column('car_spec', sa.Column('trim_id', sa.UUID(), nullable=False), schema='vehicles')
    op.add_column('car_spec', sa.Column('engine_id', sa.UUID(), nullable=True), schema='vehicles')
    op.add_column('car_spec', sa.Column('transmission_id', sa.UUID(), nullable=True), schema='vehicles')
    op.drop_constraint(op.f('car_spec_generation_id_fkey'), 'car_spec', schema='vehicles', type_='foreignkey')
    op.create_foreign_key(
        op.f('car_spec_trim_id_fkey'), 'car_spec', 'car_trim',
        ['trim_id'], ['id'],
        source_schema='vehicles', referent_schema='vehicles', ondelete='CASCADE',
    )
    op.create_foreign_key(
        op.f('car_spec_engine_id_fkey'), 'car_spec', 'vehicle_engine',
        ['engine_id'], ['id'],
        source_schema='vehicles', referent_schema='vehicles', ondelete='SET NULL',
    )
    op.create_foreign_key(
        op.f('car_spec_transmission_id_fkey'), 'car_spec', 'car_transmission',
        ['transmission_id'], ['id'],
        source_schema='vehicles', referent_schema='vehicles', ondelete='SET NULL',
    )
    op.drop_column('car_spec', 'generation_id', schema='vehicles')

    # motorcycle_spec
    op.add_column('motorcycle_spec', sa.Column('trim_id', sa.UUID(), nullable=False), schema='vehicles')
    op.add_column('motorcycle_spec', sa.Column('engine_id', sa.UUID(), nullable=True), schema='vehicles')
    op.add_column('motorcycle_spec', sa.Column('transmission_id', sa.UUID(), nullable=True), schema='vehicles')
    op.drop_constraint(op.f('motorcycle_spec_generation_id_fkey'), 'motorcycle_spec', schema='vehicles', type_='foreignkey')
    op.create_foreign_key(
        op.f('motorcycle_spec_trim_id_fkey'), 'motorcycle_spec', 'motorcycle_trim',
        ['trim_id'], ['id'],
        source_schema='vehicles', referent_schema='vehicles', ondelete='CASCADE',
    )
    op.create_foreign_key(
        op.f('motorcycle_spec_engine_id_fkey'), 'motorcycle_spec', 'vehicle_engine',
        ['engine_id'], ['id'],
        source_schema='vehicles', referent_schema='vehicles', ondelete='SET NULL',
    )
    op.create_foreign_key(
        op.f('motorcycle_spec_transmission_id_fkey'), 'motorcycle_spec', 'motorcycle_transmission',
        ['transmission_id'], ['id'],
        source_schema='vehicles', referent_schema='vehicles', ondelete='SET NULL',
    )
    op.drop_column('motorcycle_spec', 'generation_id', schema='vehicles')


def downgrade() -> None:
    """Downgrade schema."""
    # motorcycle_spec
    op.add_column('motorcycle_spec', sa.Column('generation_id', sa.UUID(), autoincrement=False, nullable=False), schema='vehicles')
    op.drop_constraint(op.f('motorcycle_spec_transmission_id_fkey'), 'motorcycle_spec', schema='vehicles', type_='foreignkey')
    op.drop_constraint(op.f('motorcycle_spec_engine_id_fkey'), 'motorcycle_spec', schema='vehicles', type_='foreignkey')
    op.drop_constraint(op.f('motorcycle_spec_trim_id_fkey'), 'motorcycle_spec', schema='vehicles', type_='foreignkey')
    op.create_foreign_key(
        op.f('motorcycle_spec_generation_id_fkey'), 'motorcycle_spec', 'vehicle_generation',
        ['generation_id'], ['id'],
        source_schema='vehicles', referent_schema='vehicles', ondelete='CASCADE',
    )
    op.drop_column('motorcycle_spec', 'transmission_id', schema='vehicles')
    op.drop_column('motorcycle_spec', 'engine_id', schema='vehicles')
    op.drop_column('motorcycle_spec', 'trim_id', schema='vehicles')

    # car_spec
    op.add_column('car_spec', sa.Column('generation_id', sa.UUID(), autoincrement=False, nullable=False), schema='vehicles')
    op.drop_constraint(op.f('car_spec_transmission_id_fkey'), 'car_spec', schema='vehicles', type_='foreignkey')
    op.drop_constraint(op.f('car_spec_engine_id_fkey'), 'car_spec', schema='vehicles', type_='foreignkey')
    op.drop_constraint(op.f('car_spec_trim_id_fkey'), 'car_spec', schema='vehicles', type_='foreignkey')
    op.create_foreign_key(
        op.f('car_spec_generation_id_fkey'), 'car_spec', 'vehicle_generation',
        ['generation_id'], ['id'],
        source_schema='vehicles', referent_schema='vehicles', ondelete='CASCADE',
    )
    op.drop_column('car_spec', 'transmission_id', schema='vehicles')
    op.drop_column('car_spec', 'engine_id', schema='vehicles')
    op.drop_column('car_spec', 'trim_id', schema='vehicles')
