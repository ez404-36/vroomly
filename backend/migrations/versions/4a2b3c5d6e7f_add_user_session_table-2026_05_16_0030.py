"""add user session table

Revision ID: 4a2b3c5d6e7f
Revises: f5a1b60cc108
Create Date: 2026-05-16 00:30:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4a2b3c5d6e7f"
down_revision: Union[str, None] = "f5a1b60cc108"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "user_session",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("token_jti", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=True
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["accounts.user.id"],
            ondelete="CASCADE",
        ),
        schema="accounts",
    )
    op.create_index(
        "ix_user_session_user_id",
        "user_session",
        ["user_id"],
        schema="accounts",
    )
    op.create_index(
        "ix_user_session_token_jti",
        "user_session",
        ["token_jti"],
        schema="accounts",
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_user_session_token_jti", table_name="user_session", schema="accounts")
    op.drop_index("ix_user_session_user_id", table_name="user_session", schema="accounts")
    op.drop_table("user_session", schema="accounts")