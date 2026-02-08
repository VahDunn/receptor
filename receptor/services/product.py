from typing import Sequence

from receptor.db.models import Product
from receptor.external_services.ai.prompts.products_prompt import PROMPT
from receptor.external_services.ai.response_schemas.products_schema import (
    ProductsResponseSchema,
    ProductItemSchema,
)
from receptor.repositories.product import ProductsRepository
from receptor.services.ai import AIService


class ProductsService:
    def __init__(
        self,
        repo: ProductsRepository,
        ai_service: AIService,
    ):
        self.prompt = PROMPT
        self.ai_service = ai_service
        self._repo = repo
        self.ai_service = ai_service

    async def create_products(self):
        ai_response: ProductsResponseSchema = await self.ai_service.get(self.prompt)
        products: Sequence[ProductItemSchema] = ai_response.items
        created = await self._repo.create_many(
            [
                Product(
                    name=product.name,
                    type_code=product.type_code,
                    unit=product.unit,
                    calories_per_unit=product.calories_per_unit,
                    price_rub=product.price_rub,
                )
                for product in products
            ]
        )
        await self._repo.db.commit()
        return created
