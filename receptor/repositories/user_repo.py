import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from receptor.db.models.user.user import User
from receptor.db.models.user.user_account import UserAccount
from receptor.db.models.user.user_identity import UserIdentity


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user: User,
    ) -> User:
        self.db.add(user)
        await self.db.flush()
        return user

    async def get_by_id(
        self,
        user_id: int,
    ) -> User | None:
        stmt = (
            sa.select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.identities),
                selectinload(User.excluded_products),
                selectinload(User.menus),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

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
                selectinload(User.identities),
                selectinload(User.excluded_products),
                selectinload(User.menus),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_identity(
        self,
        identity: UserIdentity,
    ) -> UserIdentity:
        self.db.add(identity)
        await self.db.flush()
        return identity

    async def create_account(
        self,
        account: UserAccount,
    ) -> UserAccount:
        self.db.add(account)
        await self.db.flush()
        return account
