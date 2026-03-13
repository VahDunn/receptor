from aiogram.fsm.state import State, StatesGroup


class ExcludedProductsForm(StatesGroup):
    waiting_for_search_query = State()
