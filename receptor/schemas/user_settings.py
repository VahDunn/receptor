from pydantic import BaseModel, ConfigDict, model_validator

from receptor.core.domain.marketplaces import Marketplace
from receptor.core.domain.regions import Region
from receptor.core.domain.settings_limits import (
    MIN_DAILY_KCAL,
    MIN_WEEKLY_BUDGET_RUB,
    MIN_WEEKLY_BUDGET_TOLERANCE_RUB,
)


class UserSettingsPatchSchema(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        use_enum_values=False,
        str_strip_whitespace=True,
    )

    kcal_min_per_day: int | None = None
    kcal_max_per_day: int | None = None
    max_money_rub: int | None = None
    weekly_budget_tolerance_rub: int | None = None
    region: Region | None = None
    marketplace: Marketplace | None = None
    notifications_enabled: bool | None = None

    @model_validator(mode="after")
    def validate_limits(self) -> "UserSettingsPatchSchema":
        if self.kcal_min_per_day is not None and self.kcal_min_per_day < MIN_DAILY_KCAL:
            raise ValueError(
                f"Минимум калорий в день должен быть не меньше {MIN_DAILY_KCAL}"
            )

        if self.kcal_max_per_day is not None and self.kcal_max_per_day < MIN_DAILY_KCAL:
            raise ValueError(
                f"Максимум калорий в день должен быть не меньше {MIN_DAILY_KCAL}"
            )

        if (
            self.kcal_min_per_day is not None
            and self.kcal_max_per_day is not None
            and self.kcal_min_per_day > self.kcal_max_per_day
        ):
            raise ValueError("Минимум калорий в день не может быть больше максимума")

        if (
            self.max_money_rub is not None
            and self.max_money_rub < MIN_WEEKLY_BUDGET_RUB
        ):
            raise ValueError(
                f"Недельный бюджет должен быть не меньше {MIN_WEEKLY_BUDGET_RUB} ₽"
            )

        if (
            self.weekly_budget_tolerance_rub is not None
            and self.weekly_budget_tolerance_rub < MIN_WEEKLY_BUDGET_TOLERANCE_RUB
        ):
            raise ValueError(
                "Допуск по бюджету должен быть не меньше "
                f"{MIN_WEEKLY_BUDGET_TOLERANCE_RUB} ₽"
            )

        return self


class UserSettingsOutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    kcal_min_per_day: int
    kcal_max_per_day: int
    max_money_rub: int
    weekly_budget_tolerance_rub: int
    region: Region
    marketplace: Marketplace
    notifications_enabled: bool
