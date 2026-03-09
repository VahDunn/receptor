from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📚 Мои меню")],
        [KeyboardButton(text="➕ Заказать меню")],
        [KeyboardButton(text="⬅ Назад")],
    ],
    resize_keyboard=True,
)
