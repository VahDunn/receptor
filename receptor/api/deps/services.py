from typing import TYPE_CHECKING

from fastapi import Depends

from receptor.api.deps.ai import get_ai_client
from receptor.api.deps.ai import get_menu_parser, get_products_parser
from receptor.api.deps.payment import get_yookassa
from receptor.api.deps.repos import get_product_repository, get_menu_repository, get_payment_repository
from receptor.repositories.payment_repo import PaymentRepository
from receptor.services.menu_service import MenuService
from receptor.services.product_service import ProductsService


if TYPE_CHECKING:
    from receptor.external_services.ai.parsers.default_parser import DefaultJsonAiParser
    from receptor.services.ai_service import AIService
    from receptor.repositories.product_repo import ProductRepository
    from receptor.repositories.menu_repo import MenuRepository
    from receptor.services.payment_service import PaymentService
    from receptor.external_services.ai.clients.abstract_ai_client import AbstractAiClient
    from receptor.external_services.payments.abstract_payment_provider import AbstractPaymentProvider

def get_ai_service(
    ai_client: "AbstractAiClient" = Depends(get_ai_client),
) -> AIService:
    return AIService(ai_client=ai_client)


def get_products_service(
    repo: "ProductRepository" = Depends(get_product_repository),
    ai_service: "AIService" = Depends(get_ai_service),
    parser: "DefaultJsonAiParser" = Depends(get_products_parser),
) -> ProductsService:
    return ProductsService(repo=repo, ai_service=ai_service, parser=parser)

def get_payment_service(
    repo: "PaymentRepository" = Depends(get_payment_repository),
    provider: "AbstractPaymentProvider" = Depends(get_yookassa),
) -> PaymentService:
    return PaymentService(
        repo=repo,
        provider=provider,
    )


def get_menu_service(
    repo: "MenuRepository" = Depends(get_menu_repository),
    products_service: "ProductsService" = Depends(get_products_service),
    ai_service: "AIService" = Depends(get_ai_service),
    payment_service: "PaymentService" = Depends(get_payment_service),
    parser: "DefaultJsonAiParser" = Depends(get_menu_parser),
) -> MenuService:
    return MenuService(
        products_service=products_service,
        ai_service=ai_service,
        parser=parser,
        repo=repo,
    )


def get_users_service():
    pass
