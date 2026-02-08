from typing import AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from receptor.db.engine import AsyncSessionLocal
from receptor.external_services.ai.clients.abstract_ai_client import AbstractAiClient
from receptor.external_services.ai.clients.chad_ai_client import ChadAIClient
from receptor.external_services.ai.parsers.abstract_parser import AbstractAiParser
from receptor.external_services.ai.parsers.products_parser import (
    ProductsAiResponseParser,
)
from receptor.repositories.product import ProductsRepository
from receptor.services.ai import AIService
from receptor.services.product import ProductsService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


depends_db = Depends(get_db)


async def get_ai_client(request: Request) -> ChadAIClient:
    return request.app.state.ai_client


def get_products_parser() -> ProductsAiResponseParser:
    return ProductsAiResponseParser(strict_json_only=True)


def get_products_ai_service(
    ai_client: AbstractAiClient = Depends(get_ai_client),
    parser: AbstractAiParser = Depends(get_products_parser),
) -> AIService:
    return AIService(ai_client=ai_client, parser=parser)


def get_products_repository(
    db=depends_db,
):
    return ProductsRepository(db=db)


depends_products_repository = Depends(get_products_repository)

depends_products_ai_service = Depends(get_products_ai_service)


def get_products_service(
    ai_service: AIService = depends_products_ai_service,
    repo: ProductsRepository = depends_products_repository,
):
    return ProductsService(ai_service=ai_service, repo=repo)


depends_products_service = Depends(get_products_service)
