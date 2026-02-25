from sqlalchemy.ext.asyncio import AsyncSession

from receptor.db.models import Menu


class MenuRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, menu: Menu) -> Menu:
        self.db.add(menu)
        await self.db.flush()
        return menu

    async def get(self, menu_id: int) -> Menu | None:
        return await self.db.get(Menu, menu_id)
