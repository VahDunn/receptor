import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from receptor.db.models.user.user_settings import UserSettings


class UserSettingsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(
        self,
        user_id: int,
    ) -> UserSettings | None:
        stmt = sa.select(UserSettings).where(UserSettings.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        settings: UserSettings,
    ) -> UserSettings:
        self.db.add(settings)
        await self.db.flush()
        return settings

    async def update(
        self,
        settings: UserSettings,
        *,
        data: dict,
    ) -> UserSettings:
        for field_name, value in data.items():
            setattr(settings, field_name, value)

        await self.db.flush()
        return settings
