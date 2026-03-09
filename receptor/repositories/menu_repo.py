from typing import Sequence

import sqlalchemy as sa

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from receptor.db.models import Menu, MenuProduct
from receptor.utils.errors import DatabaseError


class MenuRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, menu: Menu) -> Menu:
        self.db.add(menu)
        await self.db.flush()
        return menu

    async def get_by_id(self, menu_id: int) -> Menu | None:
        stmt = (
            sa.select(Menu)
            .where(Menu.id == menu_id)
            .options(
                selectinload(Menu.products_with_quantities).selectinload(
                    MenuProduct.product
                )
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_user(self, user_id: int) -> Sequence[Menu]:
        stmt = (
            sa.select(Menu)
            .where(Menu.user_id == user_id)
            .order_by(Menu.created_at.desc(), Menu.id.desc())
            .options(
                selectinload(Menu.products_with_quantities).selectinload(MenuProduct.product)
            )
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())