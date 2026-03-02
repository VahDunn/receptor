from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, ConfigDict

from receptor.api.schemas.product import ProductOut
from receptor.core.domain.marketplaces import Marketplace


class MenuCreateParams(BaseModel):
    user_id: int
    max_kcal: int
    min_kcal: int
    marketplace: Marketplace
    max_money: int = 10000
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
    meta: dict[str, Any]
    calorie_target: dict[str, Any]
    menu_structure: list[dict[str, Any]]
    daily_kcal_estimates: list[int]
    products_with_quantities: list[MenuProductResponseSchema] = Field(
        default_factory=list
    )
    created_at: Any | None = None
