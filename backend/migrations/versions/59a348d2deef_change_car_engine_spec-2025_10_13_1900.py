"""change car engine spec

Revision ID: 59a348d2deef
Revises: 21c045ee4df2
Create Date: 2025-10-13 19:00:41.453285

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "59a348d2deef"
down_revision: Union[str, None] = "21c045ee4df2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "car_engine_spec",
        sa.Column("valves", sa.SmallInteger(), nullable=False),
        schema="vehicles",
    )
    op.drop_column("car_engine_spec", "is_turbo", schema="vehicles")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "car_engine_spec",
        sa.Column("is_turbo", sa.BOOLEAN(), autoincrement=False, nullable=False),
        schema="vehicles",
    )
    op.drop_column("car_engine_spec", "valves", schema="vehicles")
