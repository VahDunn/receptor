"""meta_rename

Revision ID: 2cae9a1f99ef
Revises: 3712942a80ce
Create Date: 2026-03-09 19:04:54.619094
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2cae9a1f99ef"
down_revision: str | Sequence[str] | None = "3712942a80ce"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("account_entry", "meta", new_column_name="ledger_meta")
    op.alter_column("menu", "meta", new_column_name="menu_meta")
    op.alter_column("user_settings", "city", new_column_name="region")


def downgrade() -> None:
    op.alter_column("user_settings", "region", new_column_name="city")
    op.alter_column("menu", "menu_meta", new_column_name="meta")
    op.alter_column("account_entry", "ledger_meta", new_column_name="meta")
