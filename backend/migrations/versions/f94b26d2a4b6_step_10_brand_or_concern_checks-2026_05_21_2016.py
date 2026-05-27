"""step 10 brand or concern checks

Revision ID: f94b26d2a4b6
Revises: 0bd8baffd531
Create Date: 2026-05-21 20:16:10.915003

Шаг 10 из GRAPH.md: CHECK 'brand_id OR concern_id IS NOT NULL' для моделей,
у которых обе FK на бренд и концерн опциональны:
- VehicleEngine
- VehicleEnginePhaseRegulatorSystem
- CarTransmission
- MotorcycleTransmission

Без CHECK можно создать «бесхозный» узел (оба FK NULL), что некорректно
по бизнес-логике.
"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'f94b26d2a4b6'
down_revision: Union[str, None] = '0bd8baffd531'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint(
        'vehicle_engine_brand_or_concern_required',
        'vehicle_engine',
        'brand_id IS NOT NULL OR concern_id IS NOT NULL',
        schema='vehicles',
    )
    op.create_check_constraint(
        'vehicle_engine_phase_regulator_system_brand_or_concern_required',
        'vehicle_engine_phase_regulator_system',
        'brand_id IS NOT NULL OR concern_id IS NOT NULL',
        schema='vehicles',
    )
    op.create_check_constraint(
        'car_transmission_brand_or_concern_required',
        'car_transmission',
        'brand_id IS NOT NULL OR concern_id IS NOT NULL',
        schema='vehicles',
    )
    op.create_check_constraint(
        'motorcycle_transmission_brand_or_concern_required',
        'motorcycle_transmission',
        'brand_id IS NOT NULL OR concern_id IS NOT NULL',
        schema='vehicles',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        'motorcycle_transmission_brand_or_concern_required',
        'motorcycle_transmission', schema='vehicles', type_='check',
    )
    op.drop_constraint(
        'car_transmission_brand_or_concern_required',
        'car_transmission', schema='vehicles', type_='check',
    )
    op.drop_constraint(
        'vehicle_engine_phase_regulator_system_brand_or_concern_required',
        'vehicle_engine_phase_regulator_system', schema='vehicles', type_='check',
    )
    op.drop_constraint(
        'vehicle_engine_brand_or_concern_required',
        'vehicle_engine', schema='vehicles', type_='check',
    )
