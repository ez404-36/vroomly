"""step 6 numeric and year checks

Revision ID: 0bd8baffd531
Revises: 4f43d74dc3d1
Create Date: 2026-05-21 20:11:34.514561

Шаг 6 из GRAPH.md:
- Расширяем Numeric(3,2) → Numeric(4,2) для расхода/разгона
  (старая точность не вмещала реальные значения 10+).
- Добавляем CHECK на годы (production_year, start_year, end_year)
  и согласованность пробега / диапазона поколения.

CHECK-constraints не отслеживаются автогенерацией alembic, прописаны вручную.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0bd8baffd531'
down_revision: Union[str, None] = '4f43d74dc3d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_YEAR_MIN = 1885
_YEAR_MAX = 2100


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Расширение Numeric
    op.alter_column(
        'car_trim', 'avg_fuel_consumption',
        existing_type=sa.NUMERIC(precision=3, scale=2),
        type_=sa.Numeric(precision=4, scale=2),
        existing_nullable=True, schema='vehicles',
    )
    op.alter_column(
        'car_trim', 'acceleration',
        existing_type=sa.NUMERIC(precision=3, scale=2),
        type_=sa.Numeric(precision=4, scale=2),
        existing_nullable=True, schema='vehicles',
    )
    op.alter_column(
        'user_vehicle', 'avg_fuel_consumption',
        existing_type=sa.NUMERIC(precision=3, scale=2),
        type_=sa.Numeric(precision=4, scale=2),
        existing_nullable=True, schema='vehicles',
    )

    # 2. CHECK на годы и пробег для Vehicle
    op.create_check_constraint(
        'vehicle_production_year_range',
        'vehicle',
        f'production_year BETWEEN {_YEAR_MIN} AND {_YEAR_MAX}',
        schema='vehicles',
    )
    op.create_check_constraint(
        'vehicle_mileage_non_negative',
        'vehicle',
        'mileage IS NULL OR mileage >= 0',
        schema='vehicles',
    )

    # 3. CHECK на годы для VehicleGeneration
    op.create_check_constraint(
        'vehicle_generation_start_year_range',
        'vehicle_generation',
        f'start_year BETWEEN {_YEAR_MIN} AND {_YEAR_MAX}',
        schema='vehicles',
    )
    op.create_check_constraint(
        'vehicle_generation_end_year_range',
        'vehicle_generation',
        f'end_year IS NULL OR end_year BETWEEN {_YEAR_MIN} AND {_YEAR_MAX}',
        schema='vehicles',
    )
    op.create_check_constraint(
        'vehicle_generation_end_after_start',
        'vehicle_generation',
        'end_year IS NULL OR end_year >= start_year',
        schema='vehicles',
    )


def downgrade() -> None:
    """Downgrade schema."""
    # 3. Снимаем CHECK с VehicleGeneration
    op.drop_constraint('vehicle_generation_end_after_start', 'vehicle_generation', schema='vehicles', type_='check')
    op.drop_constraint('vehicle_generation_end_year_range', 'vehicle_generation', schema='vehicles', type_='check')
    op.drop_constraint('vehicle_generation_start_year_range', 'vehicle_generation', schema='vehicles', type_='check')

    # 2. Снимаем CHECK с Vehicle
    op.drop_constraint('vehicle_mileage_non_negative', 'vehicle', schema='vehicles', type_='check')
    op.drop_constraint('vehicle_production_year_range', 'vehicle', schema='vehicles', type_='check')

    # 1. Возвращаем Numeric(3,2)
    op.alter_column(
        'user_vehicle', 'avg_fuel_consumption',
        existing_type=sa.Numeric(precision=4, scale=2),
        type_=sa.NUMERIC(precision=3, scale=2),
        existing_nullable=True, schema='vehicles',
    )
    op.alter_column(
        'car_trim', 'acceleration',
        existing_type=sa.Numeric(precision=4, scale=2),
        type_=sa.NUMERIC(precision=3, scale=2),
        existing_nullable=True, schema='vehicles',
    )
    op.alter_column(
        'car_trim', 'avg_fuel_consumption',
        existing_type=sa.Numeric(precision=4, scale=2),
        type_=sa.NUMERIC(precision=3, scale=2),
        existing_nullable=True, schema='vehicles',
    )
