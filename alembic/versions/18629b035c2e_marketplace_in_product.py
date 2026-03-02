from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "18629b035c2e"
down_revision: Union[str, Sequence[str], None] = "73cdaafa69b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


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