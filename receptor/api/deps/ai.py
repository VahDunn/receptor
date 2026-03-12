import httpx
from fastapi import Depends

from receptor.api.deps.http_client import get_ai_http_client
from receptor.config import settings
from receptor.external_services.ai.clients.abstract_ai_client import AbstractAiClient
from receptor.external_services.ai.clients.chad_ai_client import ChadAIClient
from receptor.external_services.ai.parsers.default_parser import DefaultJsonAiParser
from receptor.external_services.ai.response_schemas.ai_menu_schema import (
    WeeklyMenuAiResponseSchema,
)
from receptor.external_services.ai.response_schemas.ai_products_schema import (
    ProductsAiResponseSchema,
)


def get_ai_client(
    client: "httpx.AsyncClient" = Depends(get_ai_http_client),
) -> AbstractAiClient:
    return ChadAIClient(
        client=client,
        api_key=settings.chad_api_key,
        url=settings.chad_url,
    )

def get_products_parser() -> DefaultJsonAiParser[ProductsAiResponseSchema]:
    return DefaultJsonAiParser(
        schema=ProductsAiResponseSchema,
        strict_json_only=True,
    )

def get_menu_parser() -> DefaultJsonAiParser[WeeklyMenuAiResponseSchema]:
    return DefaultJsonAiParser(
        schema=WeeklyMenuAiResponseSchema,
        strict_json_only=True,
    )
