import sqlalchemy as sa

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from receptor.db.models import Menu, MenuProduct


class MenuRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, menu: Menu) -> Menu:
        self.db.add(menu)
        await self.db.flush()
        stmt = (
            sa.select(Menu)
            .where(Menu.id == menu.id)
            .options(
                selectinload(Menu.products_with_quantities).selectinload(
                    MenuProduct.product
                )
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one()

    async def get(self, user_id: int) -> Menu | None:
        stmt = (
            sa.select(Menu)
            .where(Menu.user_id == user_id)
            .options(
                selectinload(Menu.products_with_quantities).selectinload(
                    MenuProduct.product
                )
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()
