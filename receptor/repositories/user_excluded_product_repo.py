import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from receptor.db.models import Product
from receptor.db.models.user.user import user_excluded_product


class UserExcludedProductsRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_excluded_products(
        self,
        *,
        user_id: int,
    ) -> list[Product]:
        stmt = (
            sa.select(Product)
            .join(
                user_excluded_product,
                user_excluded_product.c.product_id == Product.id,
            )
            .where(user_excluded_product.c.user_id == user_id)
            .order_by(Product.name)
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def exclude_products(
        self,
        *,
        user_id: int,
        product_ids: list[int],
    ) -> list[int]:
        if not product_ids:
            return []

        values = [
            {"user_id": user_id, "product_id": product_id} for product_id in product_ids
        ]

        stmt = (
            insert(user_excluded_product)
            .values(values)
            .on_conflict_do_nothing(
                index_elements=[
                    user_excluded_product.c.user_id,
                    user_excluded_product.c.product_id,
                ]
            )
        )

        await self.db.execute(stmt)
        return product_ids

    async def remove_excluded_products(
        self,
        *,
        user_id: int,
        product_ids: list[int],
    ) -> list[int]:
        if not product_ids:
            return []

        stmt = sa.delete(user_excluded_product).where(
            (user_excluded_product.c.user_id == user_id)
            & (user_excluded_product.c.product_id.in_(product_ids))
        )

        await self.db.execute(stmt)
        return product_ids
