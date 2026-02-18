import json

from receptor.external_services.ai.prompts.menu_prompt import build_menu_text_prompt
from receptor.services.ai_service import AIService
from receptor.services.product_service import ProductsService


class MenuService:
    def __init__(
        self,
        products_service: ProductsService,
        ai_service: AIService,
    ):
        self._products_service = products_service
        self.ai_service = ai_service
        self._prompt_builder = build_menu_text_prompt

    async def create_menu(
        self,
    ):
        products = await self._products_service.get()
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
        prompt = self._prompt_builder(products_json)
        res = await self.ai_service.get(prompt)
        print(res)
        return res
