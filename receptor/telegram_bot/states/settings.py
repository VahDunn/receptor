from aiogram.fsm.state import State, StatesGroup


class SettingsForm(StatesGroup):
    waiting_for_kcal_min = State()
    waiting_for_kcal_max = State()
    waiting_for_max_money = State()
    waiting_for_weekly_tolerance = State()
    waiting_for_region = State()
    waiting_for_marketplace = State()
    waiting_for_notifications = State()
