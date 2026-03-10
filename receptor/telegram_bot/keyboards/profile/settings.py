from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

settings_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🔥 Минимум калорий"),
            KeyboardButton(text="⚡ Максимум калорий"),
        ],
        [
            KeyboardButton(text="💸 Бюджет на неделю"),
            KeyboardButton(text="📉 Допуск по бюджету"),
        ],
        # [
        #     KeyboardButton(text="📍 Регион"),
        #     KeyboardButton(text="🛒 Магазин"),
        # ],
        # [KeyboardButton(text="🔔 Уведомления")],
        [KeyboardButton(text="⬅️ В профиль")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите настройку",
)
