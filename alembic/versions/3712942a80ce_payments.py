"""payments

Revision ID: 3712942a80ce
Revises: d3ffb7bdc644
Create Date: 2026-03-09 13:05:47.867972
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "3712942a80ce"
down_revision: Union[str, Sequence[str], None] = "d3ffb7bdc644"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


currency_code_enum = sa.Enum(
    "USD",
    "EUR",
    "RUB",
    name="currency_code",
    native_enum=False,
    create_constraint=True,
)

payment_status_enum = sa.Enum(
    "PENDING",
    "SUCCEEDED",
    "CANCELED",
    name="payment_status",
    native_enum=False,
    create_constraint=True,
)

account_entry_type_enum = sa.Enum(
    "CREDIT",
    "DEBIT",
    name="account_entry_type",
    native_enum=False,
    create_constraint=True,
)


def upgrade() -> None:
    op.create_table(
        "user_account",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "currency",
            currency_code_enum,
            nullable=False,
            server_default=sa.text("'RUB'"),
        ),
        sa.Column(
            "balance_minor",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
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
            name="fk_user_account_user_id_user",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_user_account"),
    )
    op.create_index(
        "ix_user_account_user_id",
        "user_account",
        ["user_id"],
        unique=True,
    )

    op.execute(
        sa.text(
            """
            INSERT INTO user_account (user_id, currency, balance_minor)
            SELECT u.id, 'RUB', 0
            FROM "user" u
            WHERE NOT EXISTS (
                SELECT 1
                FROM user_account ua
                WHERE ua.user_id = u.id
            )
            """
        )
    )

    op.create_table(
        "account_entry",
        sa.Column("account_id", sa.BigInteger(), nullable=False),
        sa.Column("amount_minor", sa.BigInteger(), nullable=False),
        sa.Column("currency", currency_code_enum, nullable=False),
        sa.Column("entry_type", account_entry_type_enum, nullable=False),
        sa.Column("operation_key", sa.String(), nullable=False),
        sa.Column("meta", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "amount_minor > 0",
            name="ck_entry_amount_nonzero",
        ),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["user_account.id"],
            ondelete="CASCADE",
            name="fk_account_entry_account_id_user_account",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_account_entry"),
        sa.UniqueConstraint("operation_key", name="uq_account_entry_operation_key"),
    )
    op.create_index(
        "ix_account_entry_account_id",
        "account_entry",
        ["account_id"],
        unique=False,
    )

    op.create_table(
        "account_payment",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("provider_payment_id", sa.String(), nullable=False),
        sa.Column("status", payment_status_enum, nullable=False),
        sa.Column("amount_minor", sa.BigInteger(), nullable=False),
        sa.Column("currency", currency_code_enum, nullable=False),
        sa.Column("idempotency_key", sa.String(), nullable=False),
        sa.Column("confirmation_url", sa.String(), nullable=True),
        sa.Column("raw_last_event", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "amount_minor > 0",
            name="ck_payment_amount_positive",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            ondelete="CASCADE",
            name="fk_account_payment_user_id_user",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_account_payment"),
        sa.UniqueConstraint(
            "provider",
            "provider_payment_id",
            name="uq_payment_provider_payment_id",
        ),
        sa.UniqueConstraint(
            "idempotency_key",
            name="uq_account_payment_idempotency_key",
        ),
    )
    op.create_index(
        "ix_account_payment_user_id",
        "account_payment",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_account_payment_provider",
        "account_payment",
        ["provider"],
        unique=False,
    )
    op.create_index(
        "ix_account_payment_status",
        "account_payment",
        ["status"],
        unique=False,
    )

    op.create_table(
        "processed_webhook_event",
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("event_id", sa.String(), nullable=False),
        sa.Column("provider_payment_id", sa.String(), nullable=True),
        sa.Column("event_type", sa.String(), nullable=True),
        sa.Column("raw", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_processed_webhook_event"),
        sa.UniqueConstraint(
            "provider",
            "event_id",
            name="uq_processed_webhook_provider_event_id",
        ),
    )
    op.create_index(
        "ix_processed_webhook_event_provider_payment_id",
        "processed_webhook_event",
        ["provider_payment_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_processed_webhook_event_provider_payment_id",
        table_name="processed_webhook_event",
    )
    op.drop_table("processed_webhook_event")

    op.drop_index("ix_account_payment_status", table_name="account_payment")
    op.drop_index("ix_account_payment_provider", table_name="account_payment")
    op.drop_index("ix_account_payment_user_id", table_name="account_payment")
    op.drop_table("account_payment")

    op.drop_index("ix_account_entry_account_id", table_name="account_entry")
    op.drop_table("account_entry")

    op.drop_index("ix_user_account_user_id", table_name="user_account")
    op.drop_table("user_account")