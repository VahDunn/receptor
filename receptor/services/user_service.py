from receptor.core.domain.account_payment.payments import CurrencyCode
from receptor.core.domain.user_roles import UserRole
from receptor.core.errors import DatabaseError
from receptor.db.models.user.user import User
from receptor.db.models.user.user_account import UserAccount
from receptor.db.models.user.user_identity import UserIdentity
from receptor.db.models.user.user_settings import UserSettings
from receptor.repositories.user_repo import UserRepository


class UserService:
    def __init__(self, repo: UserRepository):
        self._repo = repo

    # TODO атомарность обеспечить (для create и attach identity)
    async def create(
        self,
        *,
        name: str,
        role: UserRole = UserRole.USER,
        password_hash: str | None = None,
    ) -> User:
        try:
            user = await self._repo.create(
                User(
                    name=name,
                    role=role,
                    password_hash=password_hash,
                )
            )

            await self._repo.create_settings(UserSettings(user_id=user.id))

            await self._repo.create_account(
                UserAccount(
                    user_id=user.id,
                    currency=CurrencyCode.RUB,
                    balance_minor=0,
                )
            )

            created_user_id = user.id
            await self._repo.db.commit()

        except Exception:
            await self._repo.db.rollback()
            raise

        created = await self._repo.get_by_id(created_user_id)
        if not created:
            raise DatabaseError(f"User {created_user_id} not found after create")
        return created

    async def get_by_id(self, user_id: int) -> User:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise DatabaseError(f"User {user_id} not found")
        return user

    async def get_by_identity(
        self,
        *,
        provider: str,
        external_id: str,
    ) -> User | None:
        return await self._repo.get_by_identity(
            provider=provider,
            external_id=external_id,
        )

    async def attach_identity(
        self,
        *,
        user_id: int,
        provider: str,
        external_id: str,
        username: str | None = None,
        raw_meta: dict | None = None,
    ) -> UserIdentity:
        try:
            existing = await self._repo.get_by_identity(
                provider=provider,
                external_id=external_id,
            )
            if existing:
                raise DatabaseError(
                    f"Identity {provider}:{external_id} already attached to user {existing.id}"
                )

            user = await self._repo.get_by_id(user_id)
            if not user:
                raise DatabaseError(f"User {user_id} not found")

            identity = await self._repo.create_identity(
                UserIdentity(
                    user_id=user_id,
                    provider=provider,
                    external_id=external_id,
                    username=username,
                    raw_meta=raw_meta,
                )
            )

            await self._repo.db.commit()
            return identity

        except Exception:
            await self._repo.db.rollback()
            raise

    async def update(
        self,
        *,
        user_id: int,
        name: str | None = None,
        password_hash: str | None = None,
        role: UserRole | None = None,
    ) -> User:
        try:
            user = await self._repo.get_by_id(user_id)
            if not user:
                raise DatabaseError(f"User {user_id} not found")

            if name is not None:
                user.name = name

            if password_hash is not None:
                user.password_hash = password_hash

            if role is not None:
                user.role = role

            await self._repo.update(user)
            await self._repo.db.commit()

        except Exception:
            await self._repo.db.rollback()
            raise

        updated = await self._repo.get_by_id(user_id)
        if not updated:
            raise DatabaseError(f"User {user_id} not found after update")
        return updated

    async def get_balance(
        self,
        *,
        user_id: int,
    ) -> int:
        account = await self._repo.get_account(user_id)
        if not account:
            raise DatabaseError(f"Account for user {user_id} not found")
        return account.balance_minor

    async def get_settings(
        self,
        *,
        user_id: int,
    ) -> UserSettings:
        settings: UserSettings | None = await self._repo.get_settings(user_id)
        if not settings:
            raise DatabaseError(f"Settings for user {user_id} not found")
        return settings
