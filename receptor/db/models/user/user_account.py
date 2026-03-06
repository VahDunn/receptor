from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from receptor.core.domain.account_payment.account_entry_types import AccountEntryType
from receptor.core.domain.account_payment.payments import PaymentStatus, CurrencyCode
from receptor.db.models.base import BaseORM

if TYPE_CHECKING:
    from receptor.db.models.user.user import User

class UserAccount(BaseORM):
    __tablename__ = "user_account"

    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    currency: Mapped[CurrencyCode] = mapped_column(
        sa.Enum(
            CurrencyCode,
            name="currency_code",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
        server_default=sa.text(f"'{CurrencyCode.RUB.value}'")
    )

    balance_minor: Mapped[int] = mapped_column(
        sa.BigInteger,
        nullable=False,
        server_default="0",
    )

    user: Mapped[User] = relationship("User", back_populates="account", uselist=False)
    entries = relationship(
        "LedgerEntry",
        back_populates="account",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class LedgerEntry(BaseORM):
    __tablename__ = "account_entry"

    account_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user_account.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    amount_minor: Mapped[int] = mapped_column(sa.BigInteger, nullable=False)

    currency: Mapped[CurrencyCode] = mapped_column(
        sa.Enum(
            CurrencyCode,
            name="currency_code",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
    )

    entry_type: Mapped[AccountEntryType] = mapped_column(
        sa.Enum(
            AccountEntryType,
            name="account_entry_type",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
    )

    operation_key: Mapped[str] = mapped_column(sa.String, nullable=False, unique=True)
    meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    account = relationship("UserAccount", back_populates="entries")

    __table_args__ = (
        sa.CheckConstraint("amount_minor > 0", name="ck_entry_amount_nonzero"),
    )



class AccountPayment(BaseORM):
    __tablename__ = "account_payment"

    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    provider: Mapped[str] = mapped_column(sa.String, nullable=False, index=True)

    provider_payment_id: Mapped[str] = mapped_column(sa.String, nullable=False)

    status: Mapped[PaymentStatus] = mapped_column(
        sa.Enum(
            PaymentStatus,
            name="payment_status",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
        index=True,
    )

    amount_minor: Mapped[int] = mapped_column(sa.BigInteger, nullable=False)

    currency: Mapped[CurrencyCode] = mapped_column(
        sa.Enum(
            CurrencyCode,
            name="currency_code",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
    )

    idempotency_key: Mapped[str] = mapped_column(sa.String, nullable=False, unique=True)

    confirmation_url: Mapped[str | None] = mapped_column(sa.String, nullable=True)

    raw_last_event: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        sa.UniqueConstraint("provider", "provider_payment_id", name="uq_payment_provider_payment_id"),
        sa.CheckConstraint("amount_minor > 0", name="ck_payment_amount_positive"),
    )


class ProcessedWebhookEvent(BaseORM):
    __tablename__ = "processed_webhook_event"

    provider: Mapped[str] = mapped_column(sa.String, nullable=False)
    event_id: Mapped[str] = mapped_column(sa.String, nullable=False)

    provider_payment_id: Mapped[str | None] = mapped_column(sa.String, nullable=True, index=True)
    event_type: Mapped[str | None] = mapped_column(sa.String, nullable=True)

    raw: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        sa.UniqueConstraint("provider", "event_id", name="uq_processed_webhook_provider_event_id"),
    )