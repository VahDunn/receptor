from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📚 Мои меню")],
        [KeyboardButton(text="➕ Заказать меню")],
        [KeyboardButton(text="⬅️ На главную")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие",
)
