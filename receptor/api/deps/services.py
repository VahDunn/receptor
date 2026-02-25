from typing import TYPE_CHECKING

from fastapi import Depends

from receptor.api.deps.ai import get_ai_service
from receptor.api.deps.parsers import get_menu_parser, get_products_parser
from receptor.api.deps.repositories import get_product_repository, get_menu_repository
from receptor.services.menu_service import MenuService
from receptor.services.product_service import ProductsService


if TYPE_CHECKING:
    from receptor.external_services.ai.parsers.default_parser import DefaultJsonAiParser
    from receptor.services.ai_service import AIService
    from receptor.repositories.product_repo import ProductRepository

    from receptor.repositories.menu_repo import MenuRepository


def get_products_service(
    repo: "ProductRepository" = Depends(get_product_repository),
    ai_service: "AIService" = Depends(get_ai_service),
    parser: "DefaultJsonAiParser" = Depends(get_products_parser),
) -> ProductsService:
    return ProductsService(repo=repo, ai_service=ai_service, parser=parser)


def get_menu_service(
    repo: "MenuRepository" = Depends(get_menu_repository),
    products_service: "ProductsService" = Depends(get_products_service),
    ai_service: "AIService" = Depends(get_ai_service),
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
