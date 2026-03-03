from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    ValidationInfo,
    field_validator,
    model_validator,
)

from receptor.core.domain.product_categories import ProductTypeCode
from receptor.core.domain.units import Unit


class ProductsMetaSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    store: str
    city: str
    catalog_size: int
    created_at: datetime | None = None
    version: str | None = None

    @model_validator(mode="after")
    def validate_meta(self):
        if self.catalog_size <= 0:
            raise ValueError("catalog_size must be > 0")
        return self


class ProductItemSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    type_code: str
    unit: Unit
    calories_per_unit: int
    price_rub: int

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name must be non-empty")
        return v

    @field_validator("type_code")
    @classmethod
    def validate_type_code(cls, v: str) -> str:
        allowed = {c.code for c in ProductTypeCode}
        if v not in allowed:
            raise ValueError(f"type_code must be one of: {sorted(allowed)}")
        return v

    @field_validator("calories_per_unit")
    @classmethod
    def calories_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("calories_per_unit must be >= 0")
        return v

    @field_validator("price_rub")
    @classmethod
    def price_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("price_rub must be > 0")
        return v


class ProductsResponseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    meta: ProductsMetaSchema
    items: list[ProductItemSchema]

    @model_validator(mode="after")
    def validate_all(self, info: ValidationInfo):
        self.meta.catalog_size = len(self.items)
        names = [i.name for i in self.items]
        duplicates = {n for n in names if names.count(n) > 1}
        if duplicates:
            raise ValueError(f"Duplicate product names found: {sorted(duplicates)}")

        return self
