import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from receptor.db.models.user.user import User
from receptor.db.models.user.user_account import UserAccount
from receptor.db.models.user.user_identity import UserIdentity
from receptor.db.models.user.user_settings import UserSettings


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.flush()
        return user

    async def create_settings(self, settings: UserSettings) -> UserSettings:
        self.db.add(settings)
        await self.db.flush()
        return settings

    async def create_account(self, account: UserAccount) -> UserAccount:
        self.db.add(account)
        await self.db.flush()
        return account

    async def create_identity(self, identity: UserIdentity) -> UserIdentity:
        self.db.add(identity)
        await self.db.flush()
        return identity

    async def get_by_id(self, user_id: int) -> User | None:
        stmt = (
            sa.select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.settings),
                selectinload(User.account),
                selectinload(User.identities),
                selectinload(User.excluded_products),
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_identity(
        self,
        *,
        provider: str,
        external_id: str,
    ) -> User | None:
        stmt = (
            sa.select(User)
            .join(UserIdentity, UserIdentity.user_id == User.id)
            .where(
                UserIdentity.provider == provider,
                UserIdentity.external_id == external_id,
            )
            .options(
                selectinload(User.settings),
                selectinload(User.account),
                selectinload(User.identities),
                selectinload(User.excluded_products),
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def update(self, user: User) -> User:
        await self.db.flush()
        return user

    async def get_settings(self, user_id: int) -> UserSettings | None:
        stmt = sa.select(UserSettings).where(UserSettings.user_id == user_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_account(self, user_id: int) -> UserAccount | None:
        stmt = sa.select(UserAccount).where(UserAccount.user_id == user_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()