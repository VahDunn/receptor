from typing import Literal
from decimal import Decimal

from pydantic import BaseModel, model_validator, field_validator


class MenuMetaSchema(BaseModel):
    store: str
    city: str
    version: str | None = None


class CalorieTargetSchema(BaseModel):
    min_kcal_per_day: int
    max_kcal_per_day: int

    @model_validator(mode="after")
    def validate_range(self):
        if self.min_kcal_per_day >= self.max_kcal_per_day:
            raise ValueError("min_kcal_per_day must be < max_kcal_per_day")
        return self


class DayMenuSchema(BaseModel):
    day: int
    breakfast: list[str]
    lunch: list[str]
    dinner: list[str]

    @field_validator("day")
    @classmethod
    def validate_day(cls, v: int):
        if not 1 <= v <= 7:
            raise ValueError("day must be between 1 and 7")
        return v


UnitLiteral = Literal["g", "kg", "ml", "l", "pcs"]


class ProductQuantitySchema(BaseModel):
    product_name: str
    unit: UnitLiteral
    quantity: Decimal

    @model_validator(mode="after")
    def validate_quantity(self):
        if self.quantity <= 0:
            raise ValueError("quantity must be > 0")

        if self.unit == "pcs":
            if self.quantity != int(self.quantity):
                raise ValueError("pcs quantity must be integer")

        return self


class WeeklyMenuResponseSchema(BaseModel):
    meta: MenuMetaSchema
    calorie_target: CalorieTargetSchema

    menu_structure: list[DayMenuSchema]

    daily_kcal_estimates: list[int]

    products_with_quantities: list[ProductQuantitySchema]

    @model_validator(mode="after")
    def validate_structure(self):
        if len(self.menu_structure) != 7:
            raise ValueError("menu_structure must contain exactly 7 days")

        if len(self.daily_kcal_estimates) != 7:
            raise ValueError("daily_kcal_estimates must contain 7 values")

        days = sorted([d.day for d in self.menu_structure])
        if days != [1, 2, 3, 4, 5, 6, 7]:
            raise ValueError("days must be exactly 1..7")

        min_kcal = self.calorie_target.min_kcal_per_day
        max_kcal = self.calorie_target.max_kcal_per_day

        for kcal in self.daily_kcal_estimates:
            if kcal < (min_kcal - 200) or kcal > (max_kcal + 200):
                raise ValueError(
                    f"Daily kcal {kcal} outside allowed range with tolerance ±200"
                )

        return self
