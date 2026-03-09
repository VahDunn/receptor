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
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column(
            "role",
            sa.Enum(
                "USER",
                "ADMIN",
                name="user_role",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
            server_default=sa.text("'USER'"),
        ),
        sa.PrimaryKeyConstraint("id", name="pk_user"),
    )

    conn = op.get_bind()

    conn.execute(
        sa.text(
            """
            INSERT INTO "user" (id, name, password_hash, role)
            VALUES (1, 'system', NULL, 'ADMIN')
            ON CONFLICT (id) DO NOTHING
            """
        )
    )

    conn.execute(
        sa.text(
            """
            SELECT setval(
                           pg_get_serial_sequence('"user"', 'id'),
                           (SELECT MAX(id) FROM "user")
                   )
            """
        )
    )

    conn.execute(
        sa.text(
            """
            UPDATE menu
            SET user_id = 1
            WHERE user_id IS NULL OR user_id = 0
            """
        )
    )

    op.create_table(
        "user_settings",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "kcal_min_per_day",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("2000"),
        ),
        sa.Column(
            "kcal_max_per_day",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("2500"),
        ),
        sa.Column(
            "max_money_rub",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("10000"),
        ),
        sa.Column(
            "weekly_budget_tolerance_rub",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1000"),
        ),
        sa.Column(
            "city",
            sa.String(),
            nullable=False,
            server_default=sa.text("'Москва'"),
        ),
        sa.Column(
            "marketplace",
            sa.Enum(
                "perekrestok",
                "vkusvill",
                "pyaterochka",
                "chizhik",
                name="marketplace_enum",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
            server_default=sa.text("'perekrestok'"),
        ),
        sa.Column(
            "notifications_enabled",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            ondelete="CASCADE",
            name="fk_user_settings_user_id_user",
        ),
        sa.PrimaryKeyConstraint("user_id", name="pk_user_settings"),
    )

    op.create_table(
        "user_excluded_product",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            ondelete="CASCADE",
            name="fk_uep_user_id_user",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["product.id"],
            ondelete="RESTRICT",
            name="fk_uep_product_id_product",
        ),
        sa.PrimaryKeyConstraint(
            "user_id",
            "product_id",
            name="pk_user_excluded_product",
        ),
    )

    op.create_index(
        "ix_user_excluded_product_user_id",
        "user_excluded_product",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_user_excluded_product_product_id",
        "user_excluded_product",
        ["product_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_menu_user_id_user",
        "menu",
        "user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_table(
        "user_identity",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("external_id", sa.String(), nullable=False),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("raw_meta", sa.JSON(), nullable=True),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            ondelete="CASCADE",
            name="fk_user_identity_user_id_user",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_user_identity"),
        sa.UniqueConstraint(
            "provider",
            "external_id",
            name="uq_user_identity_provider_external_id",
        ),
    )
    op.create_index(
        "ix_user_identity_user_id",
        "user_identity",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_user_identity_user_id", table_name="user_identity")
    op.drop_table("user_identity")

    op.drop_constraint("fk_menu_user_id_user", "menu", type_="foreignkey")

    op.drop_index(
        "ix_user_excluded_product_product_id",
        table_name="user_excluded_product",
    )
    op.drop_index(
        "ix_user_excluded_product_user_id",
        table_name="user_excluded_product",
    )
    op.drop_table("user_excluded_product")

    op.drop_table("user_settings")
    op.drop_table("user")