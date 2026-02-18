from typing import Sequence

from receptor.db.models import Product
from receptor.external_services.ai.prompts.products_prompt import (
    PRODUCTS_PROMPT,
)
from receptor.external_services.ai.response_schemas.ai_products_schema import (
    ProductsResponseSchema,
    ProductItemSchema,
)
from receptor.repositories.product_repo import ProductRepository
from receptor.services.ai_service import AIService


class ProductsService:
    def __init__(
        self,
        repo: ProductRepository,
        ai_service: AIService,
    ):
        self.prompt = PRODUCTS_PROMPT
        self.ai_service = ai_service
        self._repo = repo
        self.ai_service = ai_service

    async def create_products_pool(self) -> Sequence[Product]:
        ai_response: ProductsResponseSchema = await self.ai_service.get(self.prompt)
        products: Sequence[ProductItemSchema] = ai_response.items
        created: list[Product] = await self._repo.create_many(
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

    async def get(self) -> Sequence[Product]:
        return await self._repo.get()
