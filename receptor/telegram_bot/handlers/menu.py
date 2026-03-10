from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from receptor.core.errors import DatabaseError, EntityNotFoundError
from receptor.db.models.user.user import User
from receptor.schemas.menu import MenuCreateParams
from receptor.services.menu_pdf_service import MenuPdfService
from receptor.services.menu_service import MenuService
from receptor.services.user_service import UserService
from receptor.telegram_bot.keyboards.main import main_keyboard
from receptor.telegram_bot.keyboards.menu import menu_keyboard

router = Router()


def build_menu_item_keyboard(menu_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📄 PDF",
                    callback_data=f"menu:pdf:{menu_id}",
                )
            ]
        ]
    )


@router.message(Command("menu"))
@router.message(F.text == "🍽 Меню")
async def open_menu_section(message: Message, user: User) -> None:
    await message.answer(
        "Раздел меню.",
        reply_markup=menu_keyboard,
    )


@router.message(F.text == "➕ Заказать меню")
async def generate_menu(
    message: Message,
    user: User,
    user_service: UserService,
    menu_service: MenuService,
) -> None:
    settings = await user_service.get_settings(user_id=user.id)
    excluded_ids = [product.id for product in user.excluded_products]

    payload = MenuCreateParams(
        user_id=user.id,
        min_kcal=settings.kcal_min_per_day,
        max_kcal=settings.kcal_max_per_day,
        max_money_rub=settings.max_money_rub,
        max_money_tolerance_rub=settings.weekly_budget_tolerance_rub,
        marketplace=settings.marketplace,
        excluded_products_ids=excluded_ids,
    )

    try:
        menu = await menu_service.create(payload)
    except DatabaseError as e:
        await message.answer(f"Не удалось создать меню: {e}")
        return

    await message.answer(
        "Меню успешно создано ✅\n"
        f"ID меню: {menu.id}\n"
        f"Оценка недельной стоимости: {menu.weekly_cost_estimate_rub} ₽",
        reply_markup=build_menu_item_keyboard(menu.id),
    )


@router.message(Command("menus"))
@router.message(F.text == "📚 Мои меню")
async def my_menus(
    message: Message,
    user: User,
    menu_service: MenuService,
) -> None:
    menus = await menu_service.get(user.id)

    if not menus:
        await message.answer("У Вас пока нет меню.")
        return

    await message.answer("Ваши меню:")

    for menu in menus[:10]:
        await message.answer(
            f"Меню #{menu.id}\n"
            f"💸 Стоимость: {menu.weekly_cost_estimate_rub} ₽\n"
            f"📅 Дней: {len(menu.menu_structure)}\n"
            f"🕒 Создано: {menu.created_at}",
            reply_markup=build_menu_item_keyboard(menu.id),
        )


@router.callback_query(F.data.startswith("menu:pdf:"))
async def send_menu_pdf(
    callback: CallbackQuery,
    user: User,
    menu_service: MenuService,
    menu_pdf_service: MenuPdfService,
) -> None:
    await callback.answer("Готовлю PDF...")

    try:
        menu_id = int(callback.data.split(":")[-1])
    except (TypeError, ValueError):
        if callback.message is not None:
            await callback.message.answer("Некорректный ID меню.")
        return

    try:
        menu = await menu_service.get_by_id_for_user(
            user_id=user.id,
            menu_id=menu_id,
        )
    except EntityNotFoundError:
        if callback.message is not None:
            await callback.message.answer("Меню не найдено.")
        return

    pdf_bytes = menu_pdf_service.build_pdf(menu)
    pdf = BufferedInputFile(
        pdf_bytes,
        filename=f"menu_{menu.id}.pdf",
    )

    if callback.message is not None:
        await callback.message.answer_document(
            document=pdf,
            caption=f"PDF меню #{menu.id}",
        )


@router.message(F.text == "⬅️ На главную")
async def back_to_main(message: Message, user: User) -> None:
    await message.answer(
        "Главное меню.",
        reply_markup=main_keyboard,
    )
