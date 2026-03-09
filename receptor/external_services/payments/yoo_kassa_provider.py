import base64
import json
from typing import Mapping

import httpx

from receptor.core.domain.account_payment.payments import (
    PaymentStatus,
    WebhookEventType,
)
from receptor.external_services.payments.abstract_payment_provider import (
    AbstractPaymentProvider,
    CreatePaymentRequest,
    PaymentResponse,
    WebhookEvent,
    PaymentAmount,
)


class YooKassaProvider(AbstractPaymentProvider):

    DEFAULT_API_URL = "https://api.yookassa.ru/v3/payments"

    def __init__(
        self,
        shop_id: str,
        secret_key: str,
        client: httpx.AsyncClient,
        api_url: str = DEFAULT_API_URL,
    ):
        self._shop_id = shop_id
        self._secret_key = secret_key
        self._client = client
        self._api_url = api_url

    @property
    def name(self) -> str:
        return "yookassa"

    # -------------------------
    # API
    # -------------------------

    async def create_payment(
        self,
        req: CreatePaymentRequest,
    ) -> PaymentResponse:

        payload = {
            "amount": {
                "value": f"{req.amount.amount_minor / 100:.2f}",
                "currency": req.amount.currency.value,
            },
            "capture": True,
            "description": req.description,
            "confirmation": {
                "type": "redirect",
                "return_url": req.return_url,
            },
            "metadata": req.metadata or {},
        }

        headers = {
            "Authorization": self._auth_header(),
            "Idempotence-Key": req.idempotency_key,
            "Content-Type": "application/json",
        }

        resp = await self._client.post(
            self._api_url,
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()

        data = resp.json()

        return PaymentResponse(
            provider_payment_id=data["id"],
            status=self._status_from_provider(data["status"]),
            confirmation_url=data.get("confirmation", {}).get("confirmation_url"),
        )

    async def get_payment(
        self,
        provider_payment_id: str,
    ) -> PaymentResponse:

        headers = {
            "Authorization": self._auth_header(),
        }

        resp = await self._client.get(
            f"{self._api_url}/{provider_payment_id}",
            headers=headers,
        )
        resp.raise_for_status()

        data = resp.json()

        return PaymentResponse(
            provider_payment_id=data["id"],
            status=self._status_from_provider(data["status"]),
            confirmation_url=data.get("confirmation", {}).get("confirmation_url"),
        )

    # -------------------------
    # webhook
    # -------------------------

    def parse_webhook(
        self,
        *,
        headers: Mapping[str, str],
        body: bytes,
    ) -> WebhookEvent:

        payload = json.loads(body)

        event_type = payload["event"]
        obj = payload["object"]

        status = self._status_from_provider(obj["status"])

        amount_minor = int(float(obj["amount"]["value"]) * 100)

        return WebhookEvent(
            provider_payment_id=obj["id"],
            event_type=WebhookEventType(event_type),
            status=status,
            amount=PaymentAmount(
                amount_minor=amount_minor,
                currency=obj["amount"]["currency"],
            ),
            raw=payload,
            event_id=obj.get("id"),
        )

    def _auth_header(self) -> str:
        token = base64.b64encode(
            f"{self._shop_id}:{self._secret_key}".encode()
        ).decode()
        return f"Basic {token}"

    @staticmethod
    def _status_from_provider(status: str) -> PaymentStatus:
        mapping = {
            "pending": PaymentStatus.PENDING,
            "waiting_for_capture": PaymentStatus.PENDING,
            "succeeded": PaymentStatus.SUCCEEDED,
            "canceled": PaymentStatus.CANCELED,
        }
        return mapping.get(status, PaymentStatus.PENDING)