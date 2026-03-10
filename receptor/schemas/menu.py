from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from receptor.core.domain.marketplaces import Marketplace
from receptor.schemas.product import ProductOut


class MenuCreateParams(BaseModel):
    user_id: int
    max_kcal: int
    min_kcal: int
    marketplace: Marketplace
    max_money_rub: int = 10000
    max_money_tolerance_rub: int = 500
    excluded_products_ids: list[int] = Field(default_factory=list)


class MenuProductResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    product_id: int
    unit: str
    quantity: Decimal
    product: ProductOut


class MenuOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    menu_meta: dict[str, Any]
    calorie_target: dict[str, Any]
    max_money_rub: int
    weekly_budget_tolerance_rub: int
    menu_structure: list[dict[str, Any]]
    daily_kcal_estimates: list[int]
    weekly_cost_estimate_rub: int
    products_with_quantities: list[MenuProductResponseSchema] = Field(default_factory=list)
    created_at: Any | None = None