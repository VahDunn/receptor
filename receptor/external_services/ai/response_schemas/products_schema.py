from typing import Any

from pydantic import BaseModel, Field


class ProductItemSchema(BaseModel):
    id: str | None = None
    name: str | None = None
    type_code: str | None = None
    unit: str | None = None
    priority: int = 1
    notes: str | None = None
    price_rub: int | None = None
    calories_per_unit: int | None = None


class ProductsResponseSchema(BaseModel):
    meta: dict[str, Any] = Field(default_factory=dict)
    items: list[ProductItemSchema]
