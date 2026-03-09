from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from receptor.db.models.user.user import User
from receptor.services.payment_service import PaymentService
from receptor.services.user_service import UserService
from receptor.telegram_bot.keyboards.balance import balance_keyboard

router = Router()


def format_money(balance_minor: int) -> str:
    return f"{balance_minor / 100:.2f} ₽"


@router.message(Command("balance"))
@router.message(F.text == "💰 Баланс")
async def balance_handler(
    message: Message,
    user: User,
    payment_service: PaymentService,
) -> None:
    balance_minor = await payment_service.get_balance(user_id=user.id)
    await message.answer(
        f"Твой баланс: {format_money(balance_minor)}",
        reply_markup=balance_keyboard,
    )


@router.message(F.text == "💳 Пополнить")
async def top_up_balance_handler(message: Message, user: User) -> None:
    await message.answer("Закидывай на карточку :)")


@router.message(Command("settings"))
@router.message(F.text == "⚙️ Настройки")
async def settings_handler(
    message: Message,
    user: User,
    user_service: UserService,
) -> None:
    settings = await user_service.get_settings(user_id=user.id)

    await message.answer(
        "Твои настройки:\n"
        f"• kcal min/day: {settings.kcal_min_per_day}\n"
        f"• kcal max/day: {settings.kcal_max_per_day}\n"
        f"• max money rub: {settings.max_money_rub}\n"
        f"• weekly tolerance rub: {settings.weekly_budget_tolerance_rub}\n"
        f"• city: {settings.city}\n"
        f"• marketplace: {settings.marketplace}\n"
        f"• notifications: {settings.notifications_enabled}"
    )
