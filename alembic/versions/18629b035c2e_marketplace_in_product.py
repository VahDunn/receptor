from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "18629b035c2e"
down_revision: str | Sequence[str] | None = "73cdaafa69b1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "product",
        sa.Column(
            "marketplace",
            sa.String(),
            server_default=sa.text("'Перекресток'"),
            nullable=False,
        ),
    )
    op.alter_column("product", "marketplace", server_default=None)
    op.create_index("ix_product_marketplace", "product", ["marketplace"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_product_marketplace", table_name="product")
    op.drop_column("product", "marketplace")