from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🍽 Меню")],
        [KeyboardButton(text="👤 Профиль")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие",
)
