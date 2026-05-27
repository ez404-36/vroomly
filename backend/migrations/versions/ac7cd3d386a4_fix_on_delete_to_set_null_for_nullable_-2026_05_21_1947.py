"""fix on_delete to SET NULL for nullable vehicles FKs

Revision ID: ac7cd3d386a4
Revises: 4be344cebdd3
Create Date: 2026-05-21 19:47:37.543219

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac7cd3d386a4'
down_revision: Union[str, None] = '4be344cebdd3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.

    Пересоздаём 13 nullable FK с `ondelete='SET NULL'` вместо CASCADE.
    Имена FK сохраняем по стандартному PostgreSQL-паттерну
    `<table>_<col>_fkey`, чтобы downgrade мог их найти.
    """
    # car_transmission
    op.drop_constraint(op.f('car_transmission_concern_id_fkey'), 'car_transmission', schema='vehicles', type_='foreignkey')
    op.drop_constraint(op.f('car_transmission_brand_id_fkey'), 'car_transmission', schema='vehicles', type_='foreignkey')
    op.create_foreign_key(op.f('car_transmission_concern_id_fkey'), 'car_transmission', 'vehicle_concern', ['concern_id'], ['id'], source_schema='vehicles', referent_schema='vehicles', ondelete='SET NULL')
    op.create_foreign_key(op.f('car_transmission_brand_id_fkey'), 'car_transmission', 'vehicle_brand', ['brand_id'], ['id'], source_schema='vehicles', referent_schema='vehicles', ondelete='SET NULL')
    # motorcycle_transmission
    op.drop_constraint(op.f('motorcycle_transmission_concern_id_fkey'), 'motorcycle_transmission', schema='vehicles', type_='foreignkey')
    op.drop_constraint(op.f('motorcycle_transmission_brand_id_fkey'), 'motorcycle_transmission', schema='vehicles', type_='foreignkey')
    op.create_foreign_key(op.f('motorcycle_transmission_concern_id_fkey'), 'motorcycle_transmission', 'vehicle_concern', ['concern_id'], ['id'], source_schema='vehicles', referent_schema='vehicles', ondelete='SET NULL')
    op.create_foreign_key(op.f('motorcycle_transmission_brand_id_fkey'), 'motorcycle_transmission', 'vehicle_brand', ['brand_id'], ['id'], source_schema='vehicles', referent_schema='vehicles', ondelete='SET NULL')
    # vehicle
    op.drop_constraint(op.f('vehicle_country_id_fkey'), 'vehicle', schema='vehicles', type_='foreignkey')
    op.create_foreign_key(op.f('vehicle_country_id_fkey'), 'vehicle', 'country', ['country_id'], ['id'], source_schema='vehicles', referent_schema='geo', ondelete='SET NULL')
    # vehicle_brand
    op.drop_constraint(op.f('vehicle_brand_concern_id_fkey'), 'vehicle_brand', schema='vehicles', type_='foreignkey')
    op.create_foreign_key(op.f('vehicle_brand_concern_id_fkey'), 'vehicle_brand', 'vehicle_concern', ['concern_id'], ['id'], source_schema='vehicles', referent_schema='vehicles', ondelete='SET NULL')
    # vehicle_concern
    op.drop_constraint(op.f('vehicle_concern_country_id_fkey'), 'vehicle_concern', schema='vehicles', type_='foreignkey')
    op.create_foreign_key(op.f('vehicle_concern_country_id_fkey'), 'vehicle_concern', 'country', ['country_id'], ['id'], source_schema='vehicles', referent_schema='geo', ondelete='SET NULL')
    # vehicle_engine
    op.drop_constraint(op.f('vehicle_engine_brand_id_fkey'), 'vehicle_engine', schema='vehicles', type_='foreignkey')
    op.drop_constraint(op.f('vehicle_engine_phase_regulator_system_id_fkey'), 'vehicle_engine', schema='vehicles', type_='foreignkey')
    op.drop_constraint(op.f('vehicle_engine_concern_id_fkey'), 'vehicle_engine', schema='vehicles', type_='foreignkey')
    op.create_foreign_key(op.f('vehicle_engine_concern_id_fkey'), 'vehicle_engine', 'vehicle_concern', ['concern_id'], ['id'], source_schema='vehicles', referent_schema='vehicles', ondelete='SET NULL')
    op.create_foreign_key(op.f('vehicle_engine_brand_id_fkey'), 'vehicle_engine', 'vehicle_brand', ['brand_id'], ['id'], source_schema='vehicles', referent_schema='vehicles', ondelete='SET NULL')
    op.create_foreign_key(op.f('vehicle_engine_phase_regulator_system_id_fkey'), 'vehicle_engine', 'vehicle_engine_phase_regulator_system', ['phase_regulator_system_id'], ['id'], source_schema='vehicles', referent_schema='vehicles', ondelete='SET NULL')
    # vehicle_engine_phase_regulator_system
    op.drop_constraint(op.f('vehicle_engine_phase_regulator_system_concern_id_fkey'), 'vehicle_engine_phase_regulator_system', schema='vehicles', type_='foreignkey')
    op.drop_constraint(op.f('vehicle_engine_phase_regulator_system_brand_id_fkey'), 'vehicle_engine_phase_regulator_system', schema='vehicles', type_='foreignkey')
    op.create_foreign_key(op.f('vehicle_engine_phase_regulator_system_brand_id_fkey'), 'vehicle_engine_phase_regulator_system', 'vehicle_brand', ['brand_id'], ['id'], source_schema='vehicles', referent_schema='vehicles', ondelete='SET NULL')
    op.create_foreign_key(op.f('vehicle_engine_phase_regulator_system_concern_id_fkey'), 'vehicle_engine_phase_regulator_system', 'vehicle_concern', ['concern_id'], ['id'], source_schema='vehicles', referent_schema='vehicles', ondelete='SET NULL')


def downgrade() -> None:
    """Downgrade schema. Возвращаем CASCADE для тех же FK."""
    # vehicle_engine_phase_regulator_system
    op.drop_constraint(op.f('vehicle_engine_phase_regulator_system_concern_id_fkey'), 'vehicle_engine_phase_regulator_system', schema='vehicles', type_='foreignkey')
    op.drop_constraint(op.f('vehicle_engine_phase_regulator_system_brand_id_fkey'), 'vehicle_engine_phase_regulator_system', schema='vehicles', type_='foreignkey')
    op.create_foreign_key(op.f('vehicle_engine_phase_regulator_system_brand_id_fkey'), 'vehicle_engine_phase_regulator_system', 'vehicle_brand', ['brand_id'], ['id'], source_schema='vehicles', referent_schema='vehicles', ondelete='CASCADE')
    op.create_foreign_key(op.f('vehicle_engine_phase_regulator_system_concern_id_fkey'), 'vehicle_engine_phase_regulator_system', 'vehicle_concern', ['concern_id'], ['id'], source_schema='vehicles', referent_schema='vehicles', ondelete='CASCADE')
    # vehicle_engine
    op.drop_constraint(op.f('vehicle_engine_phase_regulator_system_id_fkey'), 'vehicle_engine', schema='vehicles', type_='foreignkey')
    op.drop_constraint(op.f('vehicle_engine_brand_id_fkey'), 'vehicle_engine', schema='vehicles', type_='foreignkey')
    op.drop_constraint(op.f('vehicle_engine_concern_id_fkey'), 'vehicle_engine', schema='vehicles', type_='foreignkey')
    op.create_foreign_key(op.f('vehicle_engine_concern_id_fkey'), 'vehicle_engine', 'vehicle_concern', ['concern_id'], ['id'], source_schema='vehicles', referent_schema='vehicles', ondelete='CASCADE')
    op.create_foreign_key(op.f('vehicle_engine_phase_regulator_system_id_fkey'), 'vehicle_engine', 'vehicle_engine_phase_regulator_system', ['phase_regulator_system_id'], ['id'], source_schema='vehicles', referent_schema='vehicles', ondelete='CASCADE')
    op.create_foreign_key(op.f('vehicle_engine_brand_id_fkey'), 'vehicle_engine', 'vehicle_brand', ['brand_id'], ['id'], source_schema='vehicles', referent_schema='vehicles', ondelete='CASCADE')
    # vehicle_concern
    op.drop_constraint(op.f('vehicle_concern_country_id_fkey'), 'vehicle_concern', schema='vehicles', type_='foreignkey')
    op.create_foreign_key(op.f('vehicle_concern_country_id_fkey'), 'vehicle_concern', 'country', ['country_id'], ['id'], source_schema='vehicles', referent_schema='geo', ondelete='CASCADE')
    # vehicle_brand
    op.drop_constraint(op.f('vehicle_brand_concern_id_fkey'), 'vehicle_brand', schema='vehicles', type_='foreignkey')
    op.create_foreign_key(op.f('vehicle_brand_concern_id_fkey'), 'vehicle_brand', 'vehicle_concern', ['concern_id'], ['id'], source_schema='vehicles', referent_schema='vehicles', ondelete='CASCADE')
    # vehicle
    op.drop_constraint(op.f('vehicle_country_id_fkey'), 'vehicle', schema='vehicles', type_='foreignkey')
    op.create_foreign_key(op.f('vehicle_country_id_fkey'), 'vehicle', 'country', ['country_id'], ['id'], source_schema='vehicles', referent_schema='geo', ondelete='CASCADE')
    # motorcycle_transmission
    op.drop_constraint(op.f('motorcycle_transmission_brand_id_fkey'), 'motorcycle_transmission', schema='vehicles', type_='foreignkey')
    op.drop_constraint(op.f('motorcycle_transmission_concern_id_fkey'), 'motorcycle_transmission', schema='vehicles', type_='foreignkey')
    op.create_foreign_key(op.f('motorcycle_transmission_brand_id_fkey'), 'motorcycle_transmission', 'vehicle_brand', ['brand_id'], ['id'], source_schema='vehicles', referent_schema='vehicles', ondelete='CASCADE')
    op.create_foreign_key(op.f('motorcycle_transmission_concern_id_fkey'), 'motorcycle_transmission', 'vehicle_concern', ['concern_id'], ['id'], source_schema='vehicles', referent_schema='vehicles', ondelete='CASCADE')
    # car_transmission
    op.drop_constraint(op.f('car_transmission_brand_id_fkey'), 'car_transmission', schema='vehicles', type_='foreignkey')
    op.drop_constraint(op.f('car_transmission_concern_id_fkey'), 'car_transmission', schema='vehicles', type_='foreignkey')
    op.create_foreign_key(op.f('car_transmission_brand_id_fkey'), 'car_transmission', 'vehicle_brand', ['brand_id'], ['id'], source_schema='vehicles', referent_schema='vehicles', ondelete='CASCADE')
    op.create_foreign_key(op.f('car_transmission_concern_id_fkey'), 'car_transmission', 'vehicle_concern', ['concern_id'], ['id'], source_schema='vehicles', referent_schema='vehicles', ondelete='CASCADE')
