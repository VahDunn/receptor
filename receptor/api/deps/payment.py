import httpx
from fastapi import Depends

from receptor.api.deps.http_client import get_payments_http_client
from receptor.config import settings
from receptor.external_services.payments.yoo_kassa_provider import YooKassaProvider


def get_yookassa_provider(
    client: "httpx.AsyncClient" = Depends(get_payments_http_client),
) -> YooKassaProvider:
    return YooKassaProvider(
        shop_id=settings.yookassa_shop_id,
        secret_key=settings.yookassa_secret_key,
        client=client,
    )