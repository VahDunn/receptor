from collections.abc import Sequence
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from receptor.db.models import Product
from receptor.db.models.user.user import user_excluded_product

if TYPE_CHECKING:
    from receptor.services.dto.menu.product import ProductFilterDTO


class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_many(self, products: Sequence[Product]) -> list[Product]:
        products = list(products)
        self.db.add_all(products)
        await self.db.flush()
        return products

    async def get(
        self,
        *,
        filters: "ProductFilterDTO",
    ) -> list[Product]:
        stmt = sa.select(Product)

        conditions: list[sa.ColumnElement[bool]] = []

        simple_filters = (
            ("category", Product.type_code),
            ("marketplace", Product.marketplace),
            # ("region", Product.region), TODO добавить место под регионы
        )

        for attr, column in simple_filters:
            value = getattr(filters, attr)
            if value is not None:
                conditions.append(column == value)

        if filters.query:
            conditions.append(Product.name.ilike(f"%{filters.query}%"))

        if filters.ids:
            conditions.append(Product.id.in_(filters.ids))

        if filters.excluded_by_user_id is not None:
            conditions.append(
                ~sa.exists(
                    sa.select(1).where(
                        (user_excluded_product.c.user_id == filters.excluded_by_user_id)
                        & (user_excluded_product.c.product_id == Product.id)
                    )
                )
            )

        if conditions:
            stmt = stmt.where(*conditions)

        stmt = stmt.order_by(Product.name).limit(filters.limit).offset(filters.offset)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, product_id: int) -> Product | None:
        return await self.db.get(Product, product_id)
