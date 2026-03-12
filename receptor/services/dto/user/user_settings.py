from dataclasses import dataclass

from receptor.core.domain.marketplaces import Marketplace
from receptor.core.domain.regions import Region
from receptor.core.types import UNSET, UnsetType
from receptor.services.dto.base import DTO


@dataclass(slots=True, kw_only=True)
class UpdateUserSettingsDTO(DTO):
    kcal_min_per_day: int | None | UnsetType = UNSET
    kcal_max_per_day: int | None | UnsetType = UNSET
    max_money_rub: int | None | UnsetType = UNSET
    weekly_budget_tolerance_rub: int | None | UnsetType = UNSET
    region: Region | None | UnsetType = UNSET
    marketplace: Marketplace | None | UnsetType = UNSET
    notifications_enabled: bool | None | UnsetType = UNSET
