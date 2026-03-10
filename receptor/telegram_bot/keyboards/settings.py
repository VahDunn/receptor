from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

settings_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🔥 kcal min/day"),
            KeyboardButton(text="⚡ kcal max/day"),
        ],
        [
            KeyboardButton(text="💸 max money rub"),
            KeyboardButton(text="📉 weekly tolerance"),
        ],
        [KeyboardButton(text="🏙 city"), KeyboardButton(text="🛒 marketplace")],
        [KeyboardButton(text="🔔 notifications")],
        [KeyboardButton(text="⬅️ В профиль")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите настройку",
)
