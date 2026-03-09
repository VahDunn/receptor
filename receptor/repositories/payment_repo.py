from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from receptor.core.domain.account_payment.payments import PaymentStatus
from receptor.db.models.user.user_account import (
    AccountPayment,
    LedgerEntry,
    ProcessedWebhookEvent,
    UserAccount,
)


class PaymentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_account_by_user_id(self, user_id: int) -> UserAccount | None:
        stmt = select(UserAccount).where(UserAccount.user_id == user_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def lock_account_by_user_id(self, user_id: int) -> UserAccount | None:
        stmt = (
            select(UserAccount)
            .where(UserAccount.user_id == user_id)
            .with_for_update()
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def create_account(self, account: UserAccount) -> UserAccount:
        self.db.add(account)
        await self.db.flush()
        return account

    async def create_ledger_entry(self, entry: LedgerEntry) -> LedgerEntry:
        self.db.add(entry)
        await self.db.flush()
        return entry

    async def get_ledger_entry_by_operation_key(
        self,
        operation_key: str,
    ) -> LedgerEntry | None:
        stmt = select(LedgerEntry).where(LedgerEntry.operation_key == operation_key)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def create_payment(self, payment: AccountPayment) -> AccountPayment:
        self.db.add(payment)
        await self.db.flush()
        return payment

    async def get_payment_by_provider_payment_id(
        self,
        *,
        provider: str,
        provider_payment_id: str,
    ) -> AccountPayment | None:
        stmt = select(AccountPayment).where(
            AccountPayment.provider == provider,
            AccountPayment.provider_payment_id == provider_payment_id,
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_payment_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> AccountPayment | None:
        stmt = select(AccountPayment).where(
            AccountPayment.idempotency_key == idempotency_key,
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def update_payment_status(
        self,
        *,
        payment: AccountPayment,
        status: PaymentStatus,
        confirmation_url: str | None = None,
        raw_last_event: dict | None = None,
    ) -> AccountPayment:
        payment.status = status

        if confirmation_url is not None:
            payment.confirmation_url = confirmation_url

        if raw_last_event is not None:
            payment.raw_last_event = raw_last_event

        await self.db.flush()
        return payment

    async def get_processed_webhook_event(
        self,
        *,
        provider: str,
        event_id: str,
    ) -> ProcessedWebhookEvent | None:
        stmt = select(ProcessedWebhookEvent).where(
            ProcessedWebhookEvent.provider == provider,
            ProcessedWebhookEvent.event_id == event_id,
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def create_processed_webhook_event(
        self,
        event: ProcessedWebhookEvent,
    ) -> ProcessedWebhookEvent:
        self.db.add(event)
        await self.db.flush()
        return event