from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

balance_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💳 Пополнить")],
        [KeyboardButton(text="⬅️ В профиль")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие",
)
