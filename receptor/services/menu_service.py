import json
from dataclasses import replace
from typing import TYPE_CHECKING, Sequence

from receptor.api.schemas.menu import (
    MenuCreateParams,
    MenuOut,
)
from receptor.core.domain.units import Unit
from receptor.db.models import Menu, MenuProduct
from receptor.external_services.ai.parsers.default_parser import DefaultJsonAiParser
from receptor.external_services.ai.prompts.menu_prompt import build_menu_prompt
from receptor.external_services.ai.response_schemas.ai_menu_schema import (
    WeeklyMenuAiResponseSchema,
)
from receptor.repositories.menu_repo import MenuRepository
from receptor.services.ai_service import AIService
from receptor.services.product_service import ProductsService

if TYPE_CHECKING:
    from receptor.db.models import Product


class MenuService:
    def __init__(
        self,
        products_service: ProductsService,
        ai_service: AIService,
        parser: DefaultJsonAiParser[WeeklyMenuAiResponseSchema],
        repo: MenuRepository,
    ):
        self._products_service = products_service
        self._ai_service = ai_service
        self._parser = parser
        self._prompt_builder = build_menu_prompt
        self._repo = repo

    async def create(self, payload: MenuCreateParams) -> MenuOut:
        products: Sequence["Product"] = await self._products_service.get(
            marketplace=payload.marketplace,
            exclude_ids=payload.excluded_products_ids,
        )
        allowed_ids = tuple(p.id for p in products)
        unit_by_id = {p.id: Unit(p.unit) for p in products}

        parser = replace(
            self._parser,
            context={
                "allowed_product_ids": allowed_ids,
                "unit_by_product_id": unit_by_id,
            },
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
            marketplace=payload.marketplace,
        )

        ai_menu: WeeklyMenuAiResponseSchema = await self._ai_service.get(
            prompt, parser=parser
        )

        menu = Menu(
            meta=ai_menu.meta.model_dump(mode="json"),
            calorie_target=ai_menu.calorie_target.model_dump(mode="json"),
            menu_structure=[
                {
                    "day": d.day,
                    "breakfast": [
                        {"dish_name": dish.dish_name, "products": dish.products}
                        for dish in d.breakfast
                    ],
                    "lunch": [
                        {"dish_name": dish.dish_name, "products": dish.products}
                        for dish in d.lunch
                    ],
                    "dinner": [
                        {"dish_name": dish.dish_name, "products": dish.products}
                        for dish in d.dinner
                    ],
                }
                for d in ai_menu.menu_structure
            ],
            daily_kcal_estimates=ai_menu.daily_kcal_estimates,
        )

        menu.products_with_quantities = [
            MenuProduct(
                product_id=pq.product_id,
                unit=pq.unit.value,
                quantity=pq.quantity,
            )
            for pq in ai_menu.products_with_quantities
        ]

        created = await self._repo.create(menu)
        await self._repo.db.commit()
        return MenuOut.model_validate(created, from_attributes=True)

    async def get(self, user_id):
        menu = await self._repo.get(user_id)
        return MenuOut.model_validate(menu, from_attributes=True)
