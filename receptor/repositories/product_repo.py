from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from receptor.db.models import Product


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
        exclude_ids: Sequence[int] | None = None,
    ) -> Sequence[Product]:
        stmt = sa.select(Product)

        if exclude_ids:
            stmt = stmt.where(Product.id.notin_(exclude_ids))

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, product_id: int) -> Product | None:
        return await self.db.get(Product, product_id)
