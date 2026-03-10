from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from receptor.db.models.user.user import User
from receptor.services.accounting_service import AccountingService
from receptor.telegram_bot.keyboards.profile import balance_keyboard, profile_keyboard

router = Router()


def format_money(balance_minor: int) -> str:
    return f"{balance_minor / 100:.2f} ₽"


@router.message(Command("balance"))
@router.message(F.text == "💰 Баланс")
async def balance_handler(
    message: Message,
    user: User,
    payment_service: AccountingService,
) -> None:
    balance_minor = await payment_service.get_balance(user_id=user.id)
    await message.answer(
        f"Ваш баланс: {format_money(balance_minor)}",
        reply_markup=balance_keyboard,
    )


@router.message(F.text == "💳 Пополнить")
async def top_up_balance_handler(message: Message, user: User) -> None:
    await message.answer("Закидывай на карточку :)")


@router.message(F.text == "⬅️ В профиль")
async def back_to_profile_from_balance(message: Message) -> None:
    await message.answer(
        "Профиль. Выберите раздел:",
        reply_markup=profile_keyboard,
    )
