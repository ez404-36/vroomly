"""one to one vehicle spec with type check trigger

Revision ID: 5227f16cea20
Revises: ac7cd3d386a4
Create Date: 2026-05-21 19:54:17.585006

Гарантирует:
1. На одном Vehicle висит ровно одна CarSpec / MotorcycleSpec
   (UNIQUE(vehicle_id) на обеих таблицах).
2. Согласованность с Vehicle.vehicle_type: для записи в car_spec
   соответствующий Vehicle обязан иметь vehicle_type=1 (CAR),
   для motorcycle_spec — vehicle_type=2 (MOTORCYCLE).

Эксклюзивность по типу (одна и та же запись Vehicle не может одновременно
ссылаться и из car_spec, и из motorcycle_spec) обеспечивается косвенно:
триггер по типу не пропустит вторую вставку с тем же vehicle_id, потому
что vehicle_type у Vehicle единственный.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5227f16cea20'
down_revision: Union[str, None] = 'ac7cd3d386a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


VEHICLE_TYPE_CAR = 1
VEHICLE_TYPE_MOTORCYCLE = 2


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        'car_spec_vehicle_id_unique', 'car_spec',
        ['vehicle_id'], schema='vehicles',
    )
    op.create_unique_constraint(
        'motorcycle_spec_vehicle_id_unique', 'motorcycle_spec',
        ['vehicle_id'], schema='vehicles',
    )

    op.execute(f"""
    CREATE OR REPLACE FUNCTION vehicles.check_car_spec_vehicle_type()
    RETURNS TRIGGER AS $$
    DECLARE
        v_type smallint;
    BEGIN
        SELECT vehicle_type INTO v_type
        FROM vehicles.vehicle
        WHERE id = NEW.vehicle_id;

        IF v_type IS NULL THEN
            RAISE EXCEPTION
                'Vehicle % not found for car_spec', NEW.vehicle_id;
        END IF;

        IF v_type <> {VEHICLE_TYPE_CAR} THEN
            RAISE EXCEPTION
                'CarSpec requires Vehicle.vehicle_type=% (CAR), got % for vehicle %',
                {VEHICLE_TYPE_CAR}, v_type, NEW.vehicle_id;
        END IF;

        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    op.execute(f"""
    CREATE OR REPLACE FUNCTION vehicles.check_motorcycle_spec_vehicle_type()
    RETURNS TRIGGER AS $$
    DECLARE
        v_type smallint;
    BEGIN
        SELECT vehicle_type INTO v_type
        FROM vehicles.vehicle
        WHERE id = NEW.vehicle_id;

        IF v_type IS NULL THEN
            RAISE EXCEPTION
                'Vehicle % not found for motorcycle_spec', NEW.vehicle_id;
        END IF;

        IF v_type <> {VEHICLE_TYPE_MOTORCYCLE} THEN
            RAISE EXCEPTION
                'MotorcycleSpec requires Vehicle.vehicle_type=% (MOTORCYCLE), got % for vehicle %',
                {VEHICLE_TYPE_MOTORCYCLE}, v_type, NEW.vehicle_id;
        END IF;

        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    op.execute("""
    CREATE TRIGGER car_spec_vehicle_type_check
    BEFORE INSERT OR UPDATE OF vehicle_id ON vehicles.car_spec
    FOR EACH ROW
    EXECUTE FUNCTION vehicles.check_car_spec_vehicle_type();
    """)

    op.execute("""
    CREATE TRIGGER motorcycle_spec_vehicle_type_check
    BEFORE INSERT OR UPDATE OF vehicle_id ON vehicles.motorcycle_spec
    FOR EACH ROW
    EXECUTE FUNCTION vehicles.check_motorcycle_spec_vehicle_type();
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TRIGGER IF EXISTS motorcycle_spec_vehicle_type_check ON vehicles.motorcycle_spec;")
    op.execute("DROP TRIGGER IF EXISTS car_spec_vehicle_type_check ON vehicles.car_spec;")
    op.execute("DROP FUNCTION IF EXISTS vehicles.check_motorcycle_spec_vehicle_type();")
    op.execute("DROP FUNCTION IF EXISTS vehicles.check_car_spec_vehicle_type();")

    op.drop_constraint(
        'motorcycle_spec_vehicle_id_unique', 'motorcycle_spec',
        schema='vehicles', type_='unique',
    )
    op.drop_constraint(
        'car_spec_vehicle_id_unique', 'car_spec',
        schema='vehicles', type_='unique',
    )
