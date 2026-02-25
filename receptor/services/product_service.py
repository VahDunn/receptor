from typing import Sequence, TYPE_CHECKING

from receptor.db.models import Product

from receptor.external_services.ai.prompts.products_prompt import PRODUCTS_PROMPT
from receptor.external_services.ai.response_schemas.ai_products_schema import (
    ProductsResponseSchema,
    ProductItemSchema,
)
from receptor.repositories.product_repo import ProductRepository
from receptor.services.ai_service import AIService

if TYPE_CHECKING:
    from receptor.external_services.ai.parsers.default_parser import DefaultJsonAiParser


class ProductsService:
    def __init__(
        self,
        repo: ProductRepository,
        ai_service: AIService,
        parser: "DefaultJsonAiParser",
    ):
        self.prompt = PRODUCTS_PROMPT
        self._repo = repo
        self.ai_service = ai_service
        self._parser = parser

    async def create_products_pool(self) -> Sequence[Product]:
        ai_response: ProductsResponseSchema = await self.ai_service.get(
            self.prompt,
            parser=self._parser,
        )

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

    async def get(
        self,
        exclude_ids: Sequence[int] | None = None,
    ) -> Sequence[Product]:
        return await self._repo.get(exclude_ids=exclude_ids)
