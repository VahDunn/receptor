from receptor.core.errors import DatabaseError
from receptor.db.models.user.user_settings import UserSettings
from receptor.repositories.user_settings_repo import UserSettingsRepository
from receptor.schemas.user_settings import UserSettingsPatchSchema


class UserSettingsService:
    def __init__(self, repo: UserSettingsRepository):
        self._repo = repo

    async def create_default(
        self,
        *,
        user_id: int,
    ) -> UserSettings:
        existing = await self._repo.get_by_user_id(user_id)
        if existing:
            return existing

        settings = UserSettings(user_id=user_id)
        return await self._repo.create(settings)

    async def get(
        self,
        *,
        user_id: int,
    ) -> UserSettings:
        settings = await self._repo.get_by_user_id(user_id)
        if not settings:
            raise DatabaseError(f"Settings for user {user_id} not found")
        return settings

    async def update(
        self,
        *,
        user_id: int,
        schema: UserSettingsPatchSchema,
    ) -> UserSettings:
        settings = await self._repo.get_by_user_id(user_id)
        if not settings:
            raise DatabaseError(f"Settings for user {user_id} not found")

        update_data = schema.model_dump(exclude_unset=True)

        if not update_data:
            return settings

        return await self._repo.update(settings, data=update_data)
