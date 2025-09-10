"""init project schemas

Revision ID: cc595d2d9f77
Revises:
Create Date: 2025-08-04 01:41:10.854974

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "cc595d2d9f77"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('CREATE SCHEMA IF NOT EXISTS accounts;')
    op.execute('CREATE SCHEMA IF NOT EXISTS geo;')
    op.execute('CREATE SCHEMA IF NOT EXISTS vehicles;')


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('DROP SCHEMA IF EXISTS accounts;')
    op.execute('DROP SCHEMA IF EXISTS geo;')
    op.execute('DROP SCHEMA IF EXISTS vehicles;')
