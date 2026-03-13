from collections.abc import Sequence
from typing import TYPE_CHECKING

from receptor.core.domain.marketplaces import Marketplace
from receptor.db.models import Product
from receptor.external_services.ai.prompts.products_prompt import build_products_prompt
from receptor.external_services.ai.response_schemas.ai_products_schema import (
    ProductItemSchema,
    ProductsAiResponseSchema,
)
from receptor.repositories.product_repo import ProductRepository
from receptor.services.ai_service import AIService
from receptor.services.dto.product import ProductFilterDTO

if TYPE_CHECKING:
    from receptor.external_services.ai.parsers.default_parser import DefaultJsonAiParser


POSITIONS_NUMBER = 200
CALORIES_AMOUNT = 2500

RESPONSE_FIELDS = ["name", "type_code", "unit", "calories_per_unit", "price_rub"]


class ProductsService:
    def __init__(
        self,
        repo: ProductRepository,
        ai_service: AIService,
        parser: "DefaultJsonAiParser",
    ):
        self._repo = repo
        self.ai_service = ai_service
        self._parser = parser
        self._prompt_builder = build_products_prompt

    async def create_products_pool(self, marketplace: Marketplace) -> Sequence[Product]:
        prompt = self._prompt_builder(
            marketplace=marketplace,
            positions_number=POSITIONS_NUMBER,
            calories_amount=CALORIES_AMOUNT,
            response_fields=RESPONSE_FIELDS,
        )

        ai_response: ProductsAiResponseSchema = await self.ai_service.get(
            prompt,
            parser=self._parser,
        )

        products: Sequence[ProductItemSchema] = ai_response.items

        created: list[Product] = await self._repo.create_many(
            [
                Product(
                    name=p.name,
                    type_code=p.type_code,
                    unit=p.unit.value,
                    calories_per_unit=p.calories_per_unit,
                    price_rub=p.price_rub,
                    marketplace=marketplace.value,
                )
                for p in products
            ]
        )
        await self._repo.db.commit()
        return created

    async def get(
        self,
        *,
        filters: ProductFilterDTO,
    ) -> list[Product]:
        return await self._repo.get(filters=filters)
