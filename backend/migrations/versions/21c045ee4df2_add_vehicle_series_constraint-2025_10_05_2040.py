"""add vehicle series constraint

Revision ID: 21c045ee4df2
Revises: 1731e4b3cb70
Create Date: 2025-10-05 20:40:06.552569

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "21c045ee4df2"
down_revision: Union[str, None] = "1731e4b3cb70"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        "vehicle_series_brand_id_name_unique",
        "vehicle_series",
        ["brand_id", "name"],
        schema="vehicles",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "vehicle_series_brand_id_name_unique",
        "vehicle_series",
        schema="vehicles",
        type_="unique",
    )
