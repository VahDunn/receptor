"""create user_id in menu table

Revision ID: 73cdaafa69b1
Revises: 650e9c0da335
Create Date: 2026-02-26 10:26:37.755914

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "73cdaafa69b1"
down_revision: str | Sequence[str] | None = "650e9c0da335"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "menu",
        sa.Column(
            "user_id",
            sa.BigInteger(),
            server_default="0",
            nullable=False,
        ),
    )

    op.alter_column("menu", "user_id", server_default=None)

    op.create_index("ix_menu_user_id", "menu", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_menu_user_id", table_name="menu")
    op.drop_column("menu", "user_id")
