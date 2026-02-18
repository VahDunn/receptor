from sqlalchemy.ext.asyncio import AsyncSession


class MenuRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, menu_text: str):
        self.db.add(menu_text)
        await self.db.flush()
        return menu_text
