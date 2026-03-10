from typing import TYPE_CHECKING

from fastapi import Depends

from receptor.api.deps.ai import get_ai_client, get_menu_parser, get_products_parser
from receptor.api.deps.payment import get_yookassa_provider
from receptor.api.deps.repos import (
    get_menu_repo,
    get_payment_repo,
    get_product_repo,
    get_user_repo,
)
from receptor.services import (
    AccountingService,
    AIService,
    MenuService,
    ProductsService,
    UserService,
)

if TYPE_CHECKING:
    from receptor.external_services.ai.clients.abstract_ai_client import (
        AbstractAiClient,
    )
    from receptor.external_services.ai.parsers.default_parser import DefaultJsonAiParser
    from receptor.external_services.payments.abstract_payment_provider import (
        AbstractPaymentProvider,
    )
    from receptor.repositories import (
        MenuRepository,
        PaymentRepository,
        ProductRepository,
        UserRepository,
    )


def get_ai_service(
    ai_client: "AbstractAiClient" = Depends(get_ai_client),
) -> AIService:
    return AIService(ai_client=ai_client)


def get_products_service(
    repo: "ProductRepository" = Depends(get_product_repo),
    ai_service: "AIService" = Depends(get_ai_service),
    parser: "DefaultJsonAiParser" = Depends(get_products_parser),
) -> ProductsService:
    return ProductsService(repo=repo, ai_service=ai_service, parser=parser)

def get_payment_service(
    repo: "PaymentRepository" = Depends(get_payment_repo),
    provider: "AbstractPaymentProvider" = Depends(get_yookassa_provider),
) -> AccountingService:
    return AccountingService(
        repo=repo,
        provider=provider,
    )


def get_menu_service(
    repo: "MenuRepository" = Depends(get_menu_repo),
    products_service: "ProductsService" = Depends(get_products_service),
    ai_service: "AIService" = Depends(get_ai_service),
    payment_service: "AccountingService" = Depends(get_payment_service),
    parser: "DefaultJsonAiParser" = Depends(get_menu_parser),
) -> MenuService:
    return MenuService(
        products_service=products_service,
        ai_service=ai_service,
        parser=parser,
        repo=repo,
        payment_service=payment_service,
    )


def get_user_service(
    repo: "UserRepository" = Depends(get_user_repo),
) -> UserService:
    return UserService(repo)