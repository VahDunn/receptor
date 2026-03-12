from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from receptor.core.domain.account_payment.payments import (
    CurrencyCode,
    PaymentStatus,
    WebhookEventType,
)


@dataclass(frozen=True, slots=True)
class PaymentAmount:
    amount_minor: int
    currency: CurrencyCode


@dataclass(frozen=True, slots=True)
class CreatePaymentRequest:
    amount: PaymentAmount
    description: str
    idempotency_key: str
    return_url: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class PaymentResponse:
    provider_payment_id: str
    status: PaymentStatus
    confirmation_url: str | None = None


@dataclass(frozen=True, slots=True)
class WebhookEvent:
    provider_payment_id: str
    event_type: WebhookEventType
    status: PaymentStatus
    amount: PaymentAmount
    raw: dict[str, Any]
    event_id: str | None = None


class AbstractPaymentProvider(ABC):
    @abstractmethod
    async def create_payment(self, req: CreatePaymentRequest) -> PaymentResponse:
        """Создать платёж у провайдера."""
        raise NotImplementedError

    @abstractmethod
    async def get_payment(self, provider_payment_id: str) -> PaymentResponse:
        """Получить актуальный статус платежа у провайдера."""
        raise NotImplementedError

    @abstractmethod
    def parse_webhook(
        self,
        *,
        headers: Mapping[str, str],
        body: bytes,
    ) -> WebhookEvent:
        """Проверить подпись/валидировать и распарсить вебхук."""
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self) -> str:
        """Уникальное имя провайдера (yookassa, stripe и т.п.)"""
        raise NotImplementedError