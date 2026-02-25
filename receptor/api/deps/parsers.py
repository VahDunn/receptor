from receptor.external_services.ai.parsers.default_parser import DefaultJsonAiParser
from receptor.external_services.ai.response_schemas.ai_products_schema import (
    ProductsResponseSchema,
)
from receptor.external_services.ai.response_schemas.ai_menu_schema import (
    WeeklyMenuAiResponseSchema,
)


def get_products_parser() -> DefaultJsonAiParser[ProductsResponseSchema]:
    return DefaultJsonAiParser(
        schema=ProductsResponseSchema,
        strict_json_only=True,
    )


def get_menu_parser() -> DefaultJsonAiParser[WeeklyMenuAiResponseSchema]:
    return DefaultJsonAiParser(
        schema=WeeklyMenuAiResponseSchema,
        strict_json_only=True,
    )
