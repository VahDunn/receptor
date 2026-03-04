"""user_model

Revision ID: d3ffb7bdc644
Revises: b97511275fa0
Create Date: 2026-03-04 14:35:22.135826
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d3ffb7bdc644"
down_revision: Union[str, Sequence[str], None] = "b97511275fa0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),

        sa.Column("telegram_user_id", sa.BigInteger(), nullable=False),
        sa.Column("telegram_username", sa.String(), nullable=True),

        sa.Column("email", sa.String(), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("token_version", sa.Integer(), server_default=sa.text("0"), nullable=False),

        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),

        sa.PrimaryKeyConstraint("id", name="pk_user"),
        sa.UniqueConstraint("telegram_user_id", name="uq_user_telegram_user_id"),
        sa.UniqueConstraint("email", name="uq_user_email"),
    )

    op.create_index("ix_user_telegram_user_id", "user", ["telegram_user_id"], unique=False)
    op.create_index("ix_user_email", "user", ["email"], unique=False)

    conn = op.get_bind()

    conn.execute(sa.text("""
        INSERT INTO "user" (id, telegram_user_id, telegram_username, is_active)
        VALUES (1, 0, 'system', true)
        ON CONFLICT (id) DO NOTHING
    """))

    conn.execute(sa.text("""
        UPDATE menu
        SET user_id = 1
        WHERE user_id IS NULL OR user_id = 0
    """))

    op.create_table(
        "user_settings",
        sa.Column("user_id", sa.BigInteger(), nullable=False),

        sa.Column("kcal_min_per_day", sa.Integer(), nullable=True),
        sa.Column("kcal_max_per_day", sa.Integer(), nullable=True),

        sa.Column("max_money_rub", sa.Integer(), nullable=True),
        sa.Column("weekly_budget_tolerance_rub", sa.Integer(), nullable=True),

        sa.Column("default_city", sa.String(), nullable=True),
        sa.Column("default_store", sa.String(), nullable=True),
        sa.Column("default_marketplace", sa.String(), nullable=True),

        sa.Column("notifications_enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),

        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE", name="fk_user_settings_user_id_user"),
        sa.PrimaryKeyConstraint("user_id", name="pk_user_settings"),
    )

    op.create_table(
        "user_excluded_product",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE", name="fk_uep_user_id_user"),
        sa.ForeignKeyConstraint(["product_id"], ["product.id"], ondelete="RESTRICT", name="fk_uep_product_id_product"),
        sa.PrimaryKeyConstraint("user_id", "product_id", name="pk_user_excluded_product"),
    )

    op.create_index("ix_user_excluded_product_user_id", "user_excluded_product", ["user_id"], unique=False)
    op.create_index("ix_user_excluded_product_product_id", "user_excluded_product", ["product_id"], unique=False)

    op.create_foreign_key(
        "fk_menu_user_id_user",
        "menu",
        "user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("fk_menu_user_id_user", "menu", type_="foreignkey")

    op.drop_index("ix_user_excluded_product_product_id", table_name="user_excluded_product")
    op.drop_index("ix_user_excluded_product_user_id", table_name="user_excluded_product")
    op.drop_table("user_excluded_product")

    op.drop_table("user_settings")

    op.drop_index("ix_user_email", table_name="user")
    op.drop_index("ix_user_telegram_user_id", table_name="user")
    op.drop_table("user")