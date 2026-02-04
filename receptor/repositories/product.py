from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from receptor.db.models import Product


class ProductsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_many(self, products: Sequence[Product]) -> list[Product]:
        products = list(products)
        self.db.add_all(products)
        await self.db.flush()
        return products
