from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from receptor.api.schemas.menu import MenuCreateParams
from receptor.services.menu_service import MenuService
from receptor.services.user_service import UserService
from receptor.core.errors import DatabaseError
from receptor.telegram_bot.handlers.commons import ensure_telegram_user

router = Router()







@router.message(Command("menu"))
async def menu_handler(
    message: Message,
    user_service: UserService,
    menu_service: MenuService,
) -> None:
    user = await ensure_telegram_user(message, user_service)
    settings = await user_service.get_settings(user_id=user.id)

    missing_fields: list[str] = []
    if settings.kcal_min_per_day is None:
        missing_fields.append("kcal_min_per_day")
    if settings.kcal_max_per_day is None:
        missing_fields.append("kcal_max_per_day")
    if settings.max_money_rub is None:
        missing_fields.append("max_money_rub")
    if settings.weekly_budget_tolerance_rub is None:
        missing_fields.append("weekly_budget_tolerance_rub")
    if settings.marketplace is None:
        missing_fields.append("marketplace")

    if missing_fields:
        await message.answer(
            "Нельзя создать меню: не заполнены настройки:\n"
            + "\n".join(f"• {field}" for field in missing_fields)
        )
        return

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
    except Exception:
        await message.answer("Не удалось создать меню из-за внутренней ошибки.")
        return

    await message.answer(
        "Меню успешно создано ✅\n"
        f"ID меню: {menu.id}\n"
        f"Оценка недельной стоимости: {menu.weekly_cost_estimate_rub} ₽"
    )