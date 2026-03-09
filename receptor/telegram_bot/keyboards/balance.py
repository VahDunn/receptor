from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

balance_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💳 Пополнить")],
        [KeyboardButton(text="⬅ Назад")],
    ],
    resize_keyboard=True,
)
