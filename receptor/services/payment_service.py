from receptor.core.domain.account_payment.account_entry_meta_kind import (
    AccountEntryMetaKind,
)
from receptor.core.domain.account_payment.account_entry_meta_schema import (
    AccountEntryMeta,
    TopupMeta,
)
from receptor.core.domain.account_payment.account_entry_types import AccountEntryType
from receptor.core.domain.account_payment.payments import (
    CurrencyCode,
    PaymentStatus,
    WebhookEventType,
)
from receptor.core.domain.account_payment.pricing import PricingMinor
from receptor.core.errors import DatabaseError
from receptor.db.models.user.user_account import (
    AccountPayment,
    LedgerEntry,
    ProcessedWebhookEvent,
    UserAccount,
)
from receptor.external_services.payments.abstract_payment_provider import (
    AbstractPaymentProvider,
    CreatePaymentRequest,
    PaymentResponse,
    WebhookEvent,
)
from receptor.repositories.payment_repo import PaymentRepository


class PaymentService:
    def __init__(
        self,
        provider: AbstractPaymentProvider,
        repo: PaymentRepository,
    ):
        self._provider = provider
        self._repo = repo

    async def init_payment(
        self,
        *,
        user_id: int,
        req: CreatePaymentRequest,
    ) -> AccountPayment:
        existing = await self._repo.get_payment_by_idempotency_key(req.idempotency_key)
        if existing:
            return existing

        provider_response: PaymentResponse = await self._provider.create_payment(req)

        payment = AccountPayment(
            user_id=user_id,
            provider=self._provider.name,
            provider_payment_id=provider_response.provider_payment_id,
            status=provider_response.status,
            amount_minor=req.amount.amount_minor,
            currency=req.amount.currency,
            idempotency_key=req.idempotency_key,
            confirmation_url=provider_response.confirmation_url,
            raw_last_event=None,
        )

        try:
            created = await self._repo.create_payment(payment)
            await self._repo.db.commit()
            return created
        except Exception:
            await self._repo.db.rollback()
            raise

    async def sync_payment_status(
        self,
        *,
        provider_payment_id: str,
    ) -> AccountPayment:
        payment = await self._repo.get_payment_by_provider_payment_id(
            provider=self._provider.name,
            provider_payment_id=provider_payment_id,
        )
        if not payment:
            raise DatabaseError(
                f"Payment {self._provider.name}:{provider_payment_id} not found"
            )

        provider_response = await self._provider.get_payment(provider_payment_id)

        try:
            await self._repo.update_payment_status(
                payment=payment,
                status=provider_response.status,
                confirmation_url=provider_response.confirmation_url,
            )
            await self._repo.db.commit()
            return payment
        except Exception:
            await self._repo.db.rollback()
            raise

    async def handle_webhook(
        self,
        *,
        headers: dict[str, str],
        body: bytes,
    ) -> AccountPayment:
        event: WebhookEvent = self._provider.parse_webhook(
            headers=headers,
            body=body,
        )

        try:
            processed_payment = await self._get_already_processed_payment(event=event)
            if processed_payment is not None:
                return processed_payment

            payment = await self._repo.get_payment_by_provider_payment_id(
                provider=self._provider.name,
                provider_payment_id=event.provider_payment_id,
            )
            if not payment:
                raise DatabaseError(
                    f"Payment {self._provider.name}:{event.provider_payment_id} not found"
                )

            await self._repo.update_payment_status(
                payment=payment,
                status=event.status,
                raw_last_event=event.raw,
            )

            if event.event_id:
                await self._repo.create_processed_webhook_event(
                    ProcessedWebhookEvent(
                        provider=self._provider.name,
                        event_id=event.event_id,
                        provider_payment_id=event.provider_payment_id,
                        event_type=event.event_type.value,
                        raw=event.raw,
                    )
                )

            if self._is_successful_payment_event(event):
                await self.credit(
                    user_id=payment.user_id,
                    amount_minor=event.amount.amount_minor,
                    currency=event.amount.currency,
                    operation_key=f"payment_topup:{self._provider.name}:{event.provider_payment_id}",
                    meta=TopupMeta(
                        kind=AccountEntryMetaKind.TOPUP,
                        provider=self._provider.name,
                        external_payment_id=event.provider_payment_id,
                    ),
                )

            await self._repo.db.commit()

        except Exception:
            await self._repo.db.rollback()
            raise

        refreshed = await self._repo.get_payment_by_provider_payment_id(
            provider=self._provider.name,
            provider_payment_id=event.provider_payment_id,
        )
        if not refreshed:
            raise DatabaseError(
                f"Payment {self._provider.name}:{event.provider_payment_id} not found after webhook"
            )
        return refreshed

    async def debit(
        self,
        *,
        user_id: int,
        amount_minor: int,
        currency: CurrencyCode,
        operation_key: str,
        meta: AccountEntryMeta,
    ) -> LedgerEntry:
        existing: (
            LedgerEntry | None
        ) = await self._repo.get_ledger_entry_by_operation_key(operation_key)
        if existing:
            return existing

        account = await self._account_get_and_check(
            user_id=user_id,
            amount_minor=amount_minor,
            currency=currency,
        )
        if account.balance_minor < amount_minor:
            raise DatabaseError("Insufficient funds")

        account.balance_minor -= amount_minor

        entry = LedgerEntry(
            account_id=account.id,
            amount_minor=amount_minor,
            currency=currency,
            entry_type=AccountEntryType.DEBIT,
            operation_key=operation_key,
            ledger_meta=meta.model_dump(mode="json"),
        )
        await self._repo.create_ledger_entry(entry)
        return entry

    async def credit(
        self,
        *,
        user_id: int,
        amount_minor: int,
        currency: CurrencyCode,
        operation_key: str,
        meta: AccountEntryMeta,
    ) -> LedgerEntry:
        existing: (
            LedgerEntry | None
        ) = await self._repo.get_ledger_entry_by_operation_key(operation_key)
        if existing:
            return existing

        account = await self._account_get_and_check(
            user_id=user_id,
            amount_minor=amount_minor,
            currency=currency,
        )
        account.balance_minor += amount_minor

        entry = LedgerEntry(
            account_id=account.id,
            amount_minor=amount_minor,
            currency=currency,
            entry_type=AccountEntryType.CREDIT,
            operation_key=operation_key,
            ledger_meta=meta.model_dump(mode="json"),
        )
        await self._repo.create_ledger_entry(entry)
        return entry

    async def get_balance(
        self,
        user_id: int,
    ) -> int:
        account = await self._repo.get_account_by_user_id(user_id)
        if not account:
            raise DatabaseError(f"Account for user {user_id} not found")
        return account.balance_minor

    async def balance_is_enough(
        self,
        user_id: int,
        operation_price: PricingMinor,
    ) -> bool:
        balance_minor = await self.get_balance(user_id)
        return balance_minor >= operation_price.value

    async def _get_already_processed_payment(
        self,
        *,
        event: WebhookEvent,
    ) -> AccountPayment | None:
        if not event.event_id:
            return None

        processed = await self._repo.get_processed_webhook_event(
            provider=self._provider.name,
            event_id=event.event_id,
        )
        if not processed:
            return None

        payment = await self._repo.get_payment_by_provider_payment_id(
            provider=self._provider.name,
            provider_payment_id=event.provider_payment_id,
        )
        if not payment:
            raise DatabaseError(
                f"Payment {self._provider.name}:{event.provider_payment_id} not found"
            )
        return payment

    async def _account_get_and_check(
        self,
        user_id: int,
        amount_minor: int,
        currency: CurrencyCode,
    ) -> UserAccount:
        if amount_minor <= 0:
            raise DatabaseError("amount_minor must be positive")

        account: UserAccount | None = await self._repo.lock_account_by_user_id(user_id)
        if not account:
            raise DatabaseError(f"Account for user {user_id} not found")

        if account.currency != currency:
            raise DatabaseError(
                f"Account currency mismatch: {account.currency} != {currency}"
            )
        return account

    @staticmethod
    def _is_successful_payment_event(event: WebhookEvent) -> bool:
        return (
            event.event_type == WebhookEventType.PAYMENT_SUCCEEDED
            and event.status == PaymentStatus.SUCCEEDED
        )
