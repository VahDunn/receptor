from receptor.core.domain.user_providers import UserProvider
from receptor.core.domain.user_roles import UserRole
from receptor.core.errors import EntityNotFoundError
from receptor.db.models.user.user import User
from receptor.services.user_service import UserService


def build_telegram_display_name(
    *,
    username: str | None,
    first_name: str | None,
    last_name: str | None,
    telegram_user_id: int,
) -> str:
    full_name = " ".join(part for part in [first_name, last_name] if part).strip()

    if full_name:
        return full_name
    if username:
        return username
    return f"tg_{telegram_user_id}"


async def get_telegram_user(
    *,
    user_service: UserService,
    telegram_user_id: int,
) -> User:
    user = await user_service.get_by_identity(
        provider=UserProvider.telegram,
        external_id=str(telegram_user_id),
    )
    if not user:
        raise EntityNotFoundError(f"Telegram user {telegram_user_id} is not registered")
    return user


async def create_telegram_user(
    *,
    user_service: UserService,
    telegram_user_id: int,
    username: str | None,
    first_name: str | None,
    last_name: str | None,
) -> User:
    existing = await user_service.get_by_identity(
        provider=UserProvider.telegram,
        external_id=str(telegram_user_id),
    )
    if existing:
        return existing

    user = await user_service.create(
        name=build_telegram_display_name(
            username=username,
            first_name=first_name,
            last_name=last_name,
            telegram_user_id=telegram_user_id,
        ),
        role=UserRole.USER,
        password_hash=None,
    )

    await user_service.attach_identity(
        user_id=user.id,
        provider=UserProvider.telegram,
        external_id=str(telegram_user_id),
        username=username,
        raw_meta={
            "first_name": first_name,
            "last_name": last_name,
        },
    )

    return await user_service.get_by_id(user.id)
