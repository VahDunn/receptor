import json
from typing import TYPE_CHECKING, Sequence

from receptor.api.schemas.menu import MenuCreateParams
from receptor.external_services.ai.parsers.menu_parser import MenuAiParser
from receptor.external_services.ai.prompts.menu_prompt import build_menu_prompt
from receptor.services.ai_service import AIService
from receptor.services.product_service import ProductsService

if TYPE_CHECKING:
    from receptor.db.models import Product


class MenuService:
    def __init__(
        self,
        products_service: ProductsService,
        ai_service: AIService,
        parser: MenuAiParser,
    ):
        self._products_service = products_service
        self.ai_service = ai_service
        self._parser = parser
        self._prompt_builder = build_menu_prompt

    async def create_menu(self, payload: MenuCreateParams):
        products: Sequence["Product"] = await self._products_service.get(
            exclude_ids=payload.excluded_products_ids,  # TODO передавать только id пользователя, его настройки и исклченные продукты получать из сервиса пользователей (вероятно через get current user)
        )

        products_payload = [
            {
                "id": p.id,
                "name": p.name,
                "type_code": p.type_code,
                "unit": p.unit,
                "calories_per_unit": p.calories_per_unit,
                "price_rub": p.price_rub,
            }
            for p in products
        ]

        products_json = json.dumps(products_payload, ensure_ascii=False)

        prompt = self._prompt_builder(
            products_json,
            min_kcal=payload.min_kcal,
            max_kcal=payload.max_kcal,
        )

        res = await self.ai_service.get(
            prompt,
            parser=self._parser,
        )

        return res
