from __future__ import annotations

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


UnitLiteral = Literal["g", "kg", "ml", "l", "pcs"]


class MenuMetaSchema(BaseModel):
    store: str
    city: str
    version: str | None = None


class CalorieTargetSchema(BaseModel):
    min_kcal_per_day: int
    max_kcal_per_day: int


class MealSchema(BaseModel):
    product_ids: list[int] = Field(default_factory=list)

    @field_validator("product_ids")
    @classmethod
    def no_duplicates_in_meal(cls, v: list[int]) -> list[int]:
        if len(v) != len(set(v)):
            raise ValueError("product_ids in a meal must be unique")
        return v


class MenuDaySchema(BaseModel):
    day: int
    breakfast: MealSchema
    lunch: MealSchema
    dinner: MealSchema

    @field_validator("day")
    @classmethod
    def validate_day(cls, v: int) -> int:
        if not 1 <= v <= 7:
            raise ValueError("day must be between 1 and 7")
        return v


class ProductQuantitySchema(BaseModel):
    product_id: int
    unit: UnitLiteral
    quantity: Decimal

    @model_validator(mode="after")
    def validate_quantity(self):
        if self.quantity <= 0:
            raise ValueError("quantity must be > 0")
        if self.unit == "pcs" and self.quantity != self.quantity.to_integral_value():
            raise ValueError('For unit "pcs" quantity must be integer')
        return self


class WeeklyMenuResponseSchema(BaseModel):
    meta: MenuMetaSchema
    calorie_target: CalorieTargetSchema
    menu_days: list[MenuDaySchema]
    daily_kcal_estimates: list[int]
    products_with_quantities: list[ProductQuantitySchema]

    @model_validator(mode="after")
    def validate_all(self):
        if len(self.menu_days) != 7:
            raise ValueError("menu_days must contain exactly 7 items")

        if len(self.daily_kcal_estimates) != 7:
            raise ValueError("daily_kcal_estimates must contain 7 items")

        days = sorted(d.day for d in self.menu_days)
        if days != [1, 2, 3, 4, 5, 6, 7]:
            raise ValueError("menu_days.day must be exactly 1..7 once each")

        ids_in_menu: set[int] = set()  # type: ignore
        for d in self.menu_days:
            ids_in_menu.update(d.breakfast.product_ids)
            ids_in_menu.update(d.lunch.product_ids)
            ids_in_menu.update(d.dinner.product_ids)

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

        return self
