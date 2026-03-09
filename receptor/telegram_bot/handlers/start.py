from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from receptor.db.models.user.user import User
from receptor.services.payment_service import PaymentService
from receptor.services.user_service import UserService
from receptor.telegram_bot.keyboards.main import main_keyboard
from receptor.telegram_bot.user_resolver import create_telegram_user

router = Router()


def format_money(balance_minor: int) -> str:
    return f"{balance_minor / 100:.2f} ₽"


@router.message(Command("start"))
async def start_handler(
    message: Message,
    user_service: UserService,
    user: User | None,
) -> None:
    tg_user = message.from_user
    if tg_user is None:
        await message.answer("Не удалось определить Telegram пользователя.")
        return

    if user is None:
        user = await create_telegram_user(
            user_service=user_service,
            telegram_user_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            last_name=tg_user.last_name,
        )

    await message.answer(
        f"Привет, {user.name}!\n"
        f"Ты зарегистрирован в системе.\n"
        f"Твой internal user_id: {user.id}",
        reply_markup=main_keyboard,
    )