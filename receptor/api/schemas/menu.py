from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, ConfigDict


class MenuCreateParams(BaseModel):
    user_id: int
    max_kcal: int
    min_kcal: int
    max_money: int = 10000
    excluded_products_ids: list[int] = Field(default_factory=list)


class ProductResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type_code: str
    unit: str
    calories_per_unit: int | None = None
    price_rub: int | None = None


class MenuProductResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    unit: str
    quantity: Decimal
    product: ProductResponseSchema


class MenuResponseSchema(BaseModel):
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
