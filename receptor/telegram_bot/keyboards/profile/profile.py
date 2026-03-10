from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

profile_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💰 Баланс")],
        [KeyboardButton(text="⚙️ Настройки")],
        [KeyboardButton(text="⬅️ На главную")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите раздел",
)
