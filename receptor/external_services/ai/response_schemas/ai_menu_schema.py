from __future__ import annotations

from decimal import Decimal
from receptor.core.domain.units import Unit

from pydantic import BaseModel, Field, ValidationInfo, field_validator, model_validator


class MenuMetaSchema(BaseModel):
    store: str
    city: str
    version: str | None = None


class CalorieTargetSchema(BaseModel):
    min_kcal_per_day: int
    max_kcal_per_day: int


class DishSchema(BaseModel):
    dish_name: str
    products: list[int] = Field(default_factory=list)  # ✅ product_id

    @field_validator("dish_name")
    @classmethod
    def dish_name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("dish_name must be non-empty")
        return v

    @field_validator("products")
    @classmethod
    def products_rules(cls, v: list[int]) -> list[int]:
        if not (2 <= len(v) <= 5):
            raise ValueError("dish.products must contain 2..5 items")
        if any(pid <= 0 for pid in v):
            raise ValueError(
                "dish.products must contain positive integers (product_id)"
            )
        if len(v) != len(set(v)):
            raise ValueError("dish.products must be unique within a dish")
        return v


class MenuDaySchema(BaseModel):
    day: int
    breakfast: list[DishSchema] = Field(default_factory=list)
    lunch: list[DishSchema] = Field(default_factory=list)
    dinner: list[DishSchema] = Field(default_factory=list)

    @field_validator("day")
    @classmethod
    def validate_day(cls, v: int) -> int:
        if not 1 <= v <= 7:
            raise ValueError("day must be between 1 and 7")
        return v

    @field_validator("breakfast", "lunch", "dinner")
    @classmethod
    def validate_meal_dishes_count(cls, v: list[DishSchema]) -> list[DishSchema]:
        if not (1 <= len(v) <= 3):
            raise ValueError("each meal must contain 1..3 dishes")
        return v


class ProductQuantitySchema(BaseModel):
    product_id: int
    unit: Unit
    quantity: Decimal

    @field_validator("product_id")
    @classmethod
    def product_id_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("product_id must be > 0")
        return v

    @model_validator(mode="after")
    def validate_quantity(self):
        if self.quantity <= 0:
            raise ValueError("quantity must be > 0")
        if self.unit == Unit.pcs and self.quantity != self.quantity.to_integral_value():
            raise ValueError('For unit "pcs" quantity must be integer')
        return self


class WeeklyMenuAiResponseSchema(BaseModel):
    meta: MenuMetaSchema
    calorie_target: CalorieTargetSchema
    menu_structure: list[MenuDaySchema]
    daily_kcal_estimates: list[int]
    products_with_quantities: list[ProductQuantitySchema]

    @model_validator(mode="after")
    def validate_all(self, info: ValidationInfo):
        if len(self.menu_structure) != 7:
            raise ValueError("menu_structure must contain exactly 7 items")
        if len(self.daily_kcal_estimates) != 7:
            raise ValueError("daily_kcal_estimates must contain 7 items")

        days = sorted(d.day for d in self.menu_structure)
        if days != [1, 2, 3, 4, 5, 6, 7]:
            raise ValueError("menu_structure.day must be exactly 1..7 once each")

        ids_in_menu: set[int] = set()
        for d in self.menu_structure:
            for dish in d.breakfast + d.lunch + d.dinner:
                ids_in_menu.update(dish.products)

        ids_in_qty = {p.product_id for p in self.products_with_quantities}

        missing_qty = ids_in_menu - ids_in_qty
        if missing_qty:
            raise ValueError(
                f"products_with_quantities missing product_id(s): {sorted(missing_qty)}"
            )

        extra_qty = ids_in_qty - ids_in_menu
        if extra_qty:
            raise ValueError(
                f"products_with_quantities has unused product_id(s): {sorted(extra_qty)}"
            )

        ctx = info.context or {}

        allowed_ids = ctx.get("allowed_product_ids")
        if allowed_ids is not None:
            allowed_set = set(allowed_ids)
            unknown = (ids_in_menu | ids_in_qty) - allowed_set
            if unknown:
                raise ValueError(
                    f"AI returned product_id(s) not present in input list: {sorted(unknown)}"
                )

        unit_by_id = ctx.get("unit_by_product_id")
        if unit_by_id is not None:
            mismatched = []
            for pq in self.products_with_quantities:
                expected = unit_by_id.get(pq.product_id)
                if expected is not None and pq.unit != expected:
                    mismatched.append((pq.product_id, expected, pq.unit))
            if mismatched:
                msg = ", ".join(
                    f"{pid} expected {exp} got {got}" for pid, exp, got in mismatched
                )
                raise ValueError(f"Unit mismatch for product_id(s): {msg}")

        return self
