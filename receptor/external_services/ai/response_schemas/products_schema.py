from typing import Any

from pydantic import BaseModel, Field


class ProductItemDTO(BaseModel):
    id: str | None = None
    name_ru: str | None = None
    category: str | None = None
    pack_hint: str | None = None
    unit: str | None = None
    priority: int = 1
    notes: str | None = None
    price: str | None = None


class ProductsResponseDTO(BaseModel):
    meta: dict[str, Any] = Field(default_factory=dict)
    items: list[ProductItemDTO]


