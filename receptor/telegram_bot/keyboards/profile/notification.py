from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

notifications_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🔔 Включить уведомления"),
            KeyboardButton(text="🔕 Выключить уведомления"),
        ],
        [KeyboardButton(text="⬅️ В настройки")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие",
)
