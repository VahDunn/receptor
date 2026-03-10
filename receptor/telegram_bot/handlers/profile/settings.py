from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from receptor.db.models.user.user import User
from receptor.services.user_service import UserService
from receptor.telegram_bot.keyboards.profile import profile_keyboard
from receptor.telegram_bot.keyboards.settings import settings_keyboard

router = Router()


def render_settings(settings) -> str:
    return (
        "Ваши настройки:\n"
        f"• kcal min/day: {settings.kcal_min_per_day}\n"
        f"• kcal max/day: {settings.kcal_max_per_day}\n"
        f"• max money rub: {settings.max_money_rub}\n"
        f"• weekly tolerance rub: {settings.weekly_budget_tolerance_rub}\n"
        f"• city: {settings.region}\n"
        f"• marketplace: {settings.marketplace}\n"
        f"• notifications: {settings.notifications_enabled}"
    )


@router.message(Command("settings"))
@router.message(F.text == "⚙️ Настройки")
async def settings_handler(
    message: Message,
    user: User,
    user_service: UserService,
    state: FSMContext,
) -> None:
    await state.clear()
    settings = await user_service.get_settings(user_id=user.id)

    await message.answer(
        f"{render_settings(settings)}\n\nВыберите, что изменить:",
        reply_markup=settings_keyboard,
    )


@router.message(F.text == "⬅️ В профиль")
async def back_to_profile_from_settings(
    message: Message,
    state: FSMContext,
) -> None:
    await state.clear()
    await message.answer(
        "Профиль. Выберите раздел:",
        reply_markup=profile_keyboard,
    )
