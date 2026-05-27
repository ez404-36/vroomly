"""natural key unique indexes for transmission and phase regulator system

Revision ID: e8b1c47f6a92
Revises: d4e7a2c81b6f
Create Date: 2026-05-28 12:30:00.000000

Добавление частичных уникальных индексов на естественные ключи:

CarTransmission:
- (brand_id, type, gears, name) WHERE brand_id IS NOT NULL
- (concern_id, type, gears, name) WHERE concern_id IS NOT NULL

VehicleEnginePhaseRegulatorSystem:
- (brand_id, name, phase_regulator_type) WHERE brand_id IS NOT NULL
- (concern_id, name, phase_regulator_type) WHERE concern_id IS NOT NULL

Для обеих моделей один из brand_id / concern_id всегда NOT NULL
(гарантируется соответствующим CHECK ``*_brand_or_concern_required``),
поэтому пара частичных индексов покрывает всё пространство строк
без overlap.

Поле "name" в обоих случаях обозначает маркетинговое/семейное имя
(например, M52 для двигателей или VVT для фазорегуляторов), а
конкретная спецификация определяется дополнительными атрибутами.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8b1c47f6a92'
down_revision: Union[str, None] = 'd4e7a2c81b6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        'car_transmission_brand_type_gears_name_unique',
        'car_transmission',
        ['brand_id', 'type', 'gears', 'name'],
        unique=True,
        schema='vehicles',
        postgresql_where=sa.text('brand_id IS NOT NULL'),
    )
    op.create_index(
        'car_transmission_concern_type_gears_name_unique',
        'car_transmission',
        ['concern_id', 'type', 'gears', 'name'],
        unique=True,
        schema='vehicles',
        postgresql_where=sa.text('concern_id IS NOT NULL'),
    )
    op.create_index(
        'vehicle_engine_phase_regulator_system_brand_name_type_unique',
        'vehicle_engine_phase_regulator_system',
        ['brand_id', 'name', 'phase_regulator_type'],
        unique=True,
        schema='vehicles',
        postgresql_where=sa.text('brand_id IS NOT NULL'),
    )
    op.create_index(
        'vehicle_engine_phase_regulator_system_concern_name_type_unique',
        'vehicle_engine_phase_regulator_system',
        ['concern_id', 'name', 'phase_regulator_type'],
        unique=True,
        schema='vehicles',
        postgresql_where=sa.text('concern_id IS NOT NULL'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        'vehicle_engine_phase_regulator_system_concern_name_type_unique',
        table_name='vehicle_engine_phase_regulator_system',
        schema='vehicles',
        postgresql_where=sa.text('concern_id IS NOT NULL'),
    )
    op.drop_index(
        'vehicle_engine_phase_regulator_system_brand_name_type_unique',
        table_name='vehicle_engine_phase_regulator_system',
        schema='vehicles',
        postgresql_where=sa.text('brand_id IS NOT NULL'),
    )
    op.drop_index(
        'car_transmission_concern_type_gears_name_unique',
        table_name='car_transmission',
        schema='vehicles',
        postgresql_where=sa.text('concern_id IS NOT NULL'),
    )
    op.drop_index(
        'car_transmission_brand_type_gears_name_unique',
        table_name='car_transmission',
        schema='vehicles',
        postgresql_where=sa.text('brand_id IS NOT NULL'),
    )
