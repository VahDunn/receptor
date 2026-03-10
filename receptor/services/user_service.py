from receptor.core.domain.account_payment.payments import CurrencyCode
from receptor.core.domain.user_providers import UserProvider
from receptor.core.domain.user_roles import UserRole
from receptor.core.errors import DatabaseError
from receptor.db.models import (
    User,
    UserAccount,
    UserIdentity,
    UserSettings,
)
from receptor.repositories.user_repo import UserRepository
from receptor.services.user_settings_service import (
    UpdateUserSettingsDTO,
    UserSettingsService,
)


class UserService:
    def __init__(
        self,
        repo: UserRepository,
        user_settings_service: UserSettingsService,
    ):
        self._repo = repo
        self._user_settings_service = user_settings_service

    async def create_telegram_user(
        self,
        *,
        username: str,
        role: UserRole = UserRole.USER,
        password_hash: str | None = None,
        tg_id: int,
    ) -> User:
        created_user_id: int | None = None
        try:
            user = await self._repo.create(
                User(
                    name=username,
                    role=role,
                    password_hash=password_hash,
                )
            )
            created_user_id = user.id

            await self._user_settings_service.create_default(user_id=user.id)

            await self._repo.create_account(
                UserAccount(
                    user_id=user.id,
                    currency=CurrencyCode.RUB,
                    balance_minor=0,
                )
            )

            await self._attach_identity(
                user_id=user.id,
                provider=UserProvider.telegram,
                external_id=str(tg_id),
                username=username,
            )

            await self._repo.db.commit()

        except Exception:
            await self._repo.db.rollback()
            raise

        created = await self._repo.get_by_id(created_user_id)
        if not created:
            raise DatabaseError(f"User {created_user_id} not found after create")
        return created

    async def get_settings(
        self,
        *,
        user_id: int,
    ) -> UserSettings:
        return await self._user_settings_service.get(user_id=user_id)

    async def update_settings(
        self,
        *,
        user_id: int,
        dto: UpdateUserSettingsDTO,
    ) -> UserSettings:
        try:
            settings = await self._user_settings_service.update(
                user_id=user_id,
                dto=dto,
            )
            await self._repo.db.commit()
            return settings
        except Exception:
            await self._repo.db.rollback()
            raise

    async def get_by_id(
        self,
        user_id: int,
    ) -> User:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise DatabaseError(f"User {user_id} not found")
        return user

    async def get_by_identity(
        self,
        *,
        provider: UserProvider,
        external_id: str,
    ) -> User | None:
        return await self._repo.get_by_identity(
            provider=provider,
            external_id=external_id,
        )

    async def _attach_identity(
        self,
        *,
        user_id: int,
        provider: UserProvider,
        external_id: str,
        username: str | None = None,
    ) -> UserIdentity:
        existing: User | None = await self._repo.get_by_identity(
            provider=provider,
            external_id=external_id,
        )
        if existing:
            raise DatabaseError(
                f"Identity {provider}:{external_id} already"
                f" attached to user with ID {existing.id}: {existing.name}"
            )

        user = await self._repo.get_by_id(user_id)
        if not user:
            raise DatabaseError(f"User {user_id} not found")

        return await self._repo.create_identity(
            UserIdentity(
                user_id=user_id,
                provider=provider,
                external_id=external_id,
                username=username,
            )
        )
