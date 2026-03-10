from decimal import Decimal

from pydantic import BaseModel, Field, ValidationInfo, field_validator, model_validator

from receptor.core.domain.units import Unit


class MenuMetaSchema(BaseModel):
    store: str
    region: str
    version: str | None = None


class CalorieTargetSchema(BaseModel):
    min_kcal_per_day: int
    max_kcal_per_day: int


class DishSchema(BaseModel):
    dish_name: str
    products: list[int] = Field(default_factory=list)

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
    weekly_cost_estimate_rub: int
    products_with_quantities: list[ProductQuantitySchema]

    @model_validator(mode="after")
    def validate_all(self, info: ValidationInfo):
        if len(self.menu_structure) != 7:
            raise ValueError("menu_structure must contain exactly 7 items")
        if len(self.daily_kcal_estimates) != 7:
            raise ValueError("daily_kcal_estimates must contain 7 items")
        if self.weekly_cost_estimate_rub <= 0:
            raise ValueError("weekly_cost_estimate_rub must be > 0")

        days = sorted(d.day for d in self.menu_structure)
        if days != [1, 2, 3, 4, 5, 6, 7]:
            raise ValueError("menu_structure.day must be exactly 1..7 once each")

        ids_in_menu: set[int] = set()
        for d in self.menu_structure:
            for dish in d.breakfast + d.lunch + d.dinner:
                ids_in_menu.update(dish.products)

        ctx = info.context or {}
        unit_by_id = ctx.get("unit_by_product_id")

        ids_in_qty = {p.product_id for p in self.products_with_quantities}
        missing_qty = ids_in_menu - ids_in_qty

        if missing_qty and unit_by_id is not None:
            min_by_unit = {
                Unit.pcs: Decimal("1"),
                Unit.g: Decimal("100"),
                Unit.ml: Decimal("100"),
                Unit.kg: Decimal("0.2"),
                Unit.l: Decimal("0.2"),
            }
            fixed = list(self.products_with_quantities)
            for pid in sorted(missing_qty):
                u = unit_by_id.get(pid)
                if u is None:
                    continue
                fixed.append(
                    ProductQuantitySchema(
                        product_id=pid,
                        unit=u,
                        quantity=min_by_unit[u],
                    )
                )
            self.products_with_quantities = fixed
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

        allowed_ids = ctx.get("allowed_product_ids")
        if allowed_ids is not None:
            allowed_set = set(allowed_ids)
            unknown = (ids_in_menu | ids_in_qty) - allowed_set
            if unknown:
                raise ValueError(
                    f"AI returned product_id(s) not present in input list: {sorted(unknown)}"
                )

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

        weekly_budget = ctx.get("weekly_budget_rub")
        weekly_tol = ctx.get("weekly_budget_tolerance_rub")
        if weekly_budget is not None and weekly_tol is not None:
            lo, hi = weekly_budget - weekly_tol, weekly_budget + weekly_tol
            if not (lo <= self.weekly_cost_estimate_rub <= hi):
                raise ValueError(
                    f"weekly_cost_estimate_rub out of range [{lo},{hi}]: {self.weekly_cost_estimate_rub}"
                )

        return self
