from typing import Mapping

from receptor.external_services.payments.abstract_payment_provider import AbstractPaymentProvider, CreatePaymentRequest, \
    PaymentResponse, WebhookEvent


class YooKassaProvider(AbstractPaymentProvider):

    @property
    def name(self) -> str:
        """Уникальное имя провайдера (yookassa, stripe и т.п.)"""
        raise NotImplementedError

    async def create_payment(self, req: CreatePaymentRequest) -> PaymentResponse:
        """Создать платёж у провайдера."""
        raise NotImplementedError

    async def get_payment(self, provider_payment_id: str) -> PaymentResponse:
        """Получить актуальный статус платежа у провайдера."""
        raise NotImplementedError

    def parse_webhook(
            self,
            *,
            headers: Mapping[str, str],
            body: bytes,
    ) -> WebhookEvent:
        """Проверить подпись/валидировать и распарсить вебхук."""
        raise NotImplementedError