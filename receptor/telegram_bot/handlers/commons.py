from aiogram.types import Message

from receptor.db.models.user.user import User
from receptor.services.user_service import UserService
from receptor.core.errors import DatabaseError


async def ensure_telegram_user(
    message: Message,
    user_service: UserService,
) -> User:
    tg_user = message.from_user
    if tg_user is None:
        raise DatabaseError("Telegram user not found")

    return await user_service.get_or_create_from_telegram(
        telegram_user_id=tg_user.id,
        username=tg_user.username,
        first_name=tg_user.first_name,
        last_name=tg_user.last_name,
    )
