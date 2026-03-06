from enum import StrEnum


class PaymentStatus(StrEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    CANCELED = "canceled"


class WebhookEventType(StrEnum):
    PAYMENT_SUCCEEDED = "payment_succeeded"
    PAYMENT_CANCELED = "payment_canceled"
    PAYMENT_PENDING = "payment_pending"

class CurrencyCode(StrEnum):
    USD = "USD"
    EUR = "EUR"
    RUB = "RUB"