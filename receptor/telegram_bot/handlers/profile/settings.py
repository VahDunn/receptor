from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from receptor.core.domain.marketplaces import Marketplace
from receptor.core.domain.regions import Region
from receptor.core.errors import ValidationError
from receptor.db.models.user.user import User
from receptor.schemas.user_settings import UserSettingsPatchSchema
from receptor.services.user_service import UserService
from receptor.telegram_bot.keyboards.profile import (
    notifications_keyboard,
    profile_keyboard,
    settings_keyboard,
)
from receptor.telegram_bot.states.settings import SettingsForm

router = Router()


def _display_value(value: object) -> str:
    if value is None:
        return "—"
    return str(value)


def render_settings(settings) -> str:
    notifications_text = "Включены" if settings.notifications_enabled else "Выключены"

    return (
        "Ваши настройки:\n"
        f"• Минимум калорий в день: {_display_value(settings.kcal_min_per_day)}\n"
        f"• Максимум калорий в день: {_display_value(settings.kcal_max_per_day)}\n"
        f"• Бюджет на неделю: {_display_value(settings.max_money_rub)} ₽\n"
        f"• Допуск по бюджету: {_display_value(settings.weekly_budget_tolerance_rub)} ₽\n"
        f"• Регион: {_display_value(settings.region)}\n"
        f"• Магазин: {_display_value(settings.marketplace)}\n"
        f"• Уведомления: {notifications_text}"
    )


async def _show_settings(
    message: Message,
    *,
    user: User,
    user_service: UserService,
) -> None:
    settings = await user_service.get_settings(user_id=user.id)
    await message.answer(
        f"{render_settings(settings)}\n\nВыберите, что изменить:",
        reply_markup=settings_keyboard,
    )


def _parse_non_negative_int(text: str) -> int:
    value = int(text.strip())
    if value < 0:
        raise ValueError
    return value


def _parse_region(text: str) -> Region:
    raw = text.strip().lower()

    for region in Region:
        if raw in {region.name.lower(), region.value.lower()}:
            return region

    raise ValueError


def _parse_marketplace(text: str) -> Marketplace:
    raw = text.strip().lower()

    for marketplace in Marketplace:
        if raw in {marketplace.name.lower(), marketplace.value.lower()}:
            return marketplace

    raise ValueError


@router.message(Command("settings"))
@router.message(F.text == "⚙️ Настройки")
async def settings_handler(
    message: Message,
    user: User,
    user_service: UserService,
    state: FSMContext,
) -> None:
    await state.clear()
    await _show_settings(message, user=user, user_service=user_service)


@router.message(F.text == "⬅️ В профиль")
async def back_to_profile_from_settings(
    message: Message,
    state: FSMContext,
) -> None:
    await state.clear()
    await message.answer(
        "Профиль. Выберите раздел:",
        reply_markup=profile_keyboard,
    )


@router.message(F.text == "🔥 Минимум калорий")
async def ask_kcal_min(
    message: Message,
    state: FSMContext,
) -> None:
    await state.set_state(SettingsForm.waiting_for_kcal_min)
    await message.answer("Введите минимальное количество калорий в день.")


@router.message(SettingsForm.waiting_for_kcal_min)
async def set_kcal_min(
    message: Message,
    user: User,
    user_service: UserService,
    state: FSMContext,
) -> None:
    try:
        value = _parse_non_negative_int(message.text or "")
        await user_service.update_settings(
            user_id=user.id,
            schema=UserSettingsPatchSchema(kcal_min_per_day=value),
        )
        await state.clear()
        await message.answer("Минимум калорий обновлён.")
        await _show_settings(message, user=user, user_service=user_service)
    except ValueError:
        await message.answer("Введите неотрицательное целое число.")
    except ValidationError as e:
        await message.answer(f"Некорректные данные: {e}")


@router.message(F.text == "⚡ Максимум калорий")
async def ask_kcal_max(
    message: Message,
    state: FSMContext,
) -> None:
    await state.set_state(SettingsForm.waiting_for_kcal_max)
    await message.answer("Введите максимальное количество калорий в день.")


@router.message(SettingsForm.waiting_for_kcal_max)
async def set_kcal_max(
    message: Message,
    user: User,
    user_service: UserService,
    state: FSMContext,
) -> None:
    try:
        value = _parse_non_negative_int(message.text or "")
        await user_service.update_settings(
            user_id=user.id,
            schema=UserSettingsPatchSchema(kcal_max_per_day=value),
        )
        await state.clear()
        await message.answer("Максимум калорий обновлён.")
        await _show_settings(message, user=user, user_service=user_service)
    except ValueError:
        await message.answer("Введите неотрицательное целое число.")
    except ValidationError as e:
        await message.answer(f"Некорректные данные: {e}")


@router.message(F.text == "💸 Бюджет на неделю")
async def ask_max_money(
    message: Message,
    state: FSMContext,
) -> None:
    await state.set_state(SettingsForm.waiting_for_max_money)
    await message.answer("Введите бюджет на неделю в рублях.")


@router.message(SettingsForm.waiting_for_max_money)
async def set_max_money(
    message: Message,
    user: User,
    user_service: UserService,
    state: FSMContext,
) -> None:
    try:
        value = _parse_non_negative_int(message.text or "")
        await user_service.update_settings(
            user_id=user.id,
            schema=UserSettingsPatchSchema(max_money_rub=value),
        )
        await state.clear()
        await message.answer("Бюджет на неделю обновлён.")
        await _show_settings(message, user=user, user_service=user_service)
    except ValueError:
        await message.answer("Введите неотрицательное целое число.")
    except ValidationError as e:
        await message.answer(f"Некорректные данные: {e}")


@router.message(F.text == "📉 Допуск по бюджету")
async def ask_weekly_tolerance(
    message: Message,
    state: FSMContext,
) -> None:
    await state.set_state(SettingsForm.waiting_for_weekly_tolerance)
    await message.answer("Введите допустимое отклонение по бюджету в рублях.")


@router.message(SettingsForm.waiting_for_weekly_tolerance)
async def set_weekly_tolerance(
    message: Message,
    user: User,
    user_service: UserService,
    state: FSMContext,
) -> None:
    try:
        value = _parse_non_negative_int(message.text or "")
        await user_service.update_settings(
            user_id=user.id,
            schema=UserSettingsPatchSchema(weekly_budget_tolerance_rub=value),
        )
        await state.clear()
        await message.answer("Допуск по бюджету обновлён.")
        await _show_settings(message, user=user, user_service=user_service)
    except ValueError:
        await message.answer("Введите неотрицательное целое число.")
    except ValidationError as e:
        await message.answer(f"Некорректные данные: {e}")


@router.message(F.text == "📍 Регион")
async def ask_region(
    message: Message,
    state: FSMContext,
) -> None:
    await state.set_state(SettingsForm.waiting_for_region)
    allowed = ", ".join(region.value for region in Region)
    await message.answer(f"Введите регион.\nДоступные значения: {allowed}")


@router.message(SettingsForm.waiting_for_region)
async def set_region(
    message: Message,
    user: User,
    user_service: UserService,
    state: FSMContext,
) -> None:
    try:
        value = _parse_region(message.text or "")
        await user_service.update_settings(
            user_id=user.id,
            schema=UserSettingsPatchSchema(region=value),
        )
        await state.clear()
        await message.answer("Регион обновлён.")
        await _show_settings(message, user=user, user_service=user_service)
    except ValueError:
        allowed = ", ".join(region.value for region in Region)
        await message.answer(f"Некорректный регион.\nДоступные значения: {allowed}")
    except ValidationError as e:
        await message.answer(f"Некорректные данные: {e}")


@router.message(F.text == "🛒 Магазин")
async def ask_marketplace(
    message: Message,
    state: FSMContext,
) -> None:
    await state.set_state(SettingsForm.waiting_for_marketplace)
    allowed = ", ".join(marketplace.value for marketplace in Marketplace)
    await message.answer(f"Введите магазин.\nДоступные значения: {allowed}")


@router.message(SettingsForm.waiting_for_marketplace)
async def set_marketplace(
    message: Message,
    user: User,
    user_service: UserService,
    state: FSMContext,
) -> None:
    try:
        value = _parse_marketplace(message.text or "")
        await user_service.update_settings(
            user_id=user.id,
            schema=UserSettingsPatchSchema(marketplace=value),
        )
        await state.clear()
        await message.answer("Магазин обновлён.")
        await _show_settings(message, user=user, user_service=user_service)
    except ValueError:
        allowed = ", ".join(marketplace.value for marketplace in Marketplace)
        await message.answer(f"Некорректный магазин.\nДоступные значения: {allowed}")
    except ValidationError as e:
        await message.answer(f"Некорректные данные: {e}")


@router.message(F.text == "🔔 Уведомления")
async def ask_notifications(
    message: Message,
    state: FSMContext,
) -> None:
    await state.set_state(SettingsForm.waiting_for_notifications)
    await message.answer(
        "Выберите режим уведомлений:",
        reply_markup=notifications_keyboard,
    )


@router.message(
    SettingsForm.waiting_for_notifications,
    F.text == "🔔 Включить уведомления",
)
async def enable_notifications(
    message: Message,
    user: User,
    user_service: UserService,
    state: FSMContext,
) -> None:
    await user_service.update_settings(
        user_id=user.id,
        schema=UserSettingsPatchSchema(notifications_enabled=True),
    )
    await state.clear()
    await message.answer("Уведомления включены.")
    await _show_settings(message, user=user, user_service=user_service)


@router.message(
    SettingsForm.waiting_for_notifications,
    F.text == "🔕 Выключить уведомления",
)
async def disable_notifications(
    message: Message,
    user: User,
    user_service: UserService,
    state: FSMContext,
) -> None:
    await user_service.update_settings(
        user_id=user.id,
        schema=UserSettingsPatchSchema(notifications_enabled=False),
    )
    await state.clear()
    await message.answer("Уведомления выключены.")
    await _show_settings(message, user=user, user_service=user_service)


@router.message(
    SettingsForm.waiting_for_notifications,
    F.text == "⬅️ В настройки",
)
async def back_from_notifications(
    message: Message,
    user: User,
    user_service: UserService,
    state: FSMContext,
) -> None:
    await state.clear()
    await _show_settings(message, user=user, user_service=user_service)
