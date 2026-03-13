from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from receptor.telegram_bot.handlers.profile.balance import router as balance_router
from receptor.telegram_bot.handlers.profile.excluded_products import (
    router as excluded_products_router,
)
from receptor.telegram_bot.handlers.profile.settings import router as settings_router
from receptor.telegram_bot.keyboards.main import main_keyboard
from receptor.telegram_bot.keyboards.profile import profile_keyboard

router = Router()

router.include_router(balance_router)
router.include_router(settings_router)
router.include_router(excluded_products_router)


@router.message(Command("profile"))
@router.message(F.text == "👤 Профиль")
async def profile_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Профиль. Выберите раздел:",
        reply_markup=profile_keyboard,
    )


@router.message(F.text == "⬅️ На главную")
async def back_to_main_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Главное меню.",
        reply_markup=main_keyboard,
    )
