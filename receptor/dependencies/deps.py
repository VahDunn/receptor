from typing import AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from receptor.db.engine import AsyncSessionLocal
from receptor.external_services.ai.clients.abstract_ai_client import AbstractAiClient
from receptor.external_services.ai.clients.chad_ai_client import ChadAIClient
from receptor.external_services.ai.parsers.abstract_parser import AbstractAiParser
from receptor.external_services.ai.parsers.menu_parser import MenuAiResponseParser
from receptor.external_services.ai.parsers.products_parser import (
    ProductsAiResponseParser,
)
from receptor.repositories.product_repo import ProductRepository
from receptor.services.ai_service import AIService
from receptor.services.menu_service import MenuService
from receptor.services.product_service import ProductsService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


depends_db = Depends(get_db)


async def get_ai_client(request: Request) -> ChadAIClient:
    return request.app.state.ai_client


def get_products_parser() -> ProductsAiResponseParser:
    return ProductsAiResponseParser(strict_json_only=True)


def get_menu_parser() -> MenuAiResponseParser:
    return MenuAiResponseParser()


def get_products_ai_service(
    ai_client: AbstractAiClient = Depends(get_ai_client),
    parser: AbstractAiParser = Depends(get_products_parser),
) -> AIService:
    return AIService(ai_client=ai_client, parser=parser)


def get_menu_ai_service(
    ai_client: AbstractAiClient = Depends(get_ai_client),
    parser: AbstractAiParser = Depends(get_menu_parser),
):
    return AIService(ai_client=ai_client, parser=parser)


def get_products_repository(
    db=depends_db,
):
    return ProductRepository(db=db)


depends_products_repository = Depends(get_products_repository)

depends_products_ai_service = Depends(get_products_ai_service)


def get_products_service(
    ai_service: AIService = depends_products_ai_service,
    repo: ProductRepository = depends_products_repository,
):
    return ProductsService(ai_service=ai_service, repo=repo)


depends_products_service = Depends(get_products_service)

depends_menu_ai_service = Depends(get_menu_ai_service)


def get_menus_service(
    ai_service: AIService = depends_menu_ai_service,
    products_service: ProductsService = depends_products_service,
):
    return MenuService(ai_service=ai_service, products_service=products_service)


depends_menus_service = Depends(get_menus_service)
