from dataclasses import dataclass

from receptor.core.domain.marketplaces import Marketplace
from receptor.core.domain.regions import Region
from receptor.core.errors import DatabaseError, ValidationError
from receptor.core.types import UNSET, UnsetType
from receptor.db.models.user.user_settings import UserSettings
from receptor.repositories.user_settings_repo import UserSettingsRepository


@dataclass(slots=True, kw_only=True)
class UpdateUserSettingsDTO:
    kcal_min_per_day: int | None | UnsetType = UNSET
    kcal_max_per_day: int | None | UnsetType = UNSET
    max_money_rub: int | None | UnsetType = UNSET
    weekly_budget_tolerance_rub: int | None | UnsetType = UNSET
    region: Region | None | UnsetType = UNSET
    marketplace: Marketplace | None | UnsetType = UNSET
    notifications_enabled: bool | UnsetType = UNSET

    def to_update_dict(self) -> dict:
        data = {
            "kcal_min_per_day": self.kcal_min_per_day,
            "kcal_max_per_day": self.kcal_max_per_day,
            "max_money_rub": self.max_money_rub,
            "weekly_budget_tolerance_rub": self.weekly_budget_tolerance_rub,
            "city": self.region,
            "marketplace": self.marketplace,
            "notifications_enabled": self.notifications_enabled,
        }

        return {k: v for k, v in data.items() if not isinstance(v, UnsetType)}


class UserSettingsService:
    def __init__(self, repo: UserSettingsRepository):
        self._repo = repo

    async def create_default(
        self,
        *,
        user_id: int,
    ) -> UserSettings:
        existing = await self._repo.get_by_user_id(user_id)
        if existing:
            return existing

        settings = UserSettings(user_id=user_id)
        return await self._repo.create(settings)

    async def get(
        self,
        *,
        user_id: int,
    ) -> UserSettings:
        settings = await self._repo.get_by_user_id(user_id)
        if not settings:
            raise DatabaseError(f"Settings for user {user_id} not found")
        return settings

    async def update(
        self,
        *,
        user_id: int,
        dto: UpdateUserSettingsDTO,
    ) -> UserSettings:
        settings = await self._repo.get_by_user_id(user_id)
        if not settings:
            raise DatabaseError(f"Settings for user {user_id} not found")

        update_data = dto.model_dump(exclude_unset=True)

        merged = self._merged_settings_snapshot(
            settings=settings,
            update_data=update_data,
        )
        self._validate_business_rules(merged)

        return await self._repo.update(settings, data=update_data)

    @staticmethod
    def _merged_settings_snapshot(
        *,
        settings: UserSettings,
        update_data: dict,
    ) -> dict:
        return {
            "kcal_min_per_day": update_data.get(
                "kcal_min_per_day",
                settings.kcal_min_per_day,
            ),
            "kcal_max_per_day": update_data.get(
                "kcal_max_per_day",
                settings.kcal_max_per_day,
            ),
            "max_money_rub": update_data.get(
                "max_money_rub",
                settings.max_money_rub,
            ),
            "weekly_budget_tolerance_rub": update_data.get(
                "weekly_budget_tolerance_rub",
                settings.weekly_budget_tolerance_rub,
            ),
            "city": update_data.get("city", settings.region),
            "marketplace": update_data.get("marketplace", settings.marketplace),
            "notifications_enabled": update_data.get(
                "notifications_enabled",
                settings.notifications_enabled,
            ),
        }

    @staticmethod
    def _validate_business_rules(data: dict) -> None:
        min_kcal = data["kcal_min_per_day"]
        max_kcal = data["kcal_max_per_day"]

        if min_kcal is not None and max_kcal is not None and min_kcal > max_kcal:
            raise ValidationError("kcal_min_per_day must be <= kcal_max_per_day")
