from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from receptor.services.payment_service import PaymentService
from receptor.services.user_service import UserService
from receptor.telegram_bot.handlers.commons import ensure_telegram_user

router = Router()

def format_money(balance_minor: int) -> str:
    return f"{balance_minor / 100:.2f} ₽"


@router.message(Command("start"))
async def start_handler(message: Message, user_service: UserService) -> None:
    user = await ensure_telegram_user(message, user_service)
    await message.answer(
        f"Привет, {user.name}!\n"
        f"Ты зарегистрирован в системе.\n"
        f"Твой internal user_id: {user.id}"
    )


@router.message(Command("balance"))
async def balance_handler(
    message: Message,
    user_service: UserService,
    payment_service: PaymentService,
) -> None:
    user = await ensure_telegram_user(message, user_service)
    balance_minor = await payment_service.get_balance(user_id=user.id)
    await message.answer(f"Твой баланс: {format_money(balance_minor)}")


@router.message(Command("settings"))
async def settings_handler(
    message: Message,
    user_service: UserService,
) -> None:
    user = await ensure_telegram_user(message, user_service)
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