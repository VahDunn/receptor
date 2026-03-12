from dataclasses import dataclass, field

from receptor.core.domain.marketplaces import Marketplace
from receptor.core.domain.product_categories import ProductTypeCode
from receptor.core.domain.regions import Region
from receptor.services.dto.base import DTO


@dataclass(slots=True, kw_only=True)
class ProductFilterDTO(DTO):
    query: str | None = None
    category: ProductTypeCode | None = None
    marketplace: Marketplace | None = None
    region: Region | None = None

    ids: list[int] = field(default_factory=list)

    excluded_by_user_id: int | None = None

    limit: int = 20
    offset: int = 0
