from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

excluded_products_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔎 Найти по названию")],
        [KeyboardButton(text="📂 Выбрать по категории")],
        [KeyboardButton(text="📋 Мои исключения")],
        [KeyboardButton(text="⬅️ В профиль")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие",
)
