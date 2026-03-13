from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from receptor.core.domain.product_categories import ProductTypeCode
from receptor.db.models import Product
from receptor.db.models.user.user import User
from receptor.services.dto.product import ProductFilterDTO
from receptor.services.menu.product_service import ProductsService
from receptor.services.user.user_excluded_products_service import (
    UserExcludedProductsService,
)
from receptor.telegram_bot.keyboards.profile import profile_keyboard
from receptor.telegram_bot.keyboards.profile.excluded_products import (
    excluded_products_keyboard,
)
from receptor.telegram_bot.states.excluded_products import ExcludedProductsForm

router = Router()


def build_product_toggle_keyboard(
    *,
    product_id: int,
    is_excluded: bool,
) -> InlineKeyboardMarkup:
    action_text = "➖ Вернуть" if is_excluded else "🚫 Исключить"
    action = "remove" if is_excluded else "add"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=action_text,
                    callback_data=f"excluded_product:{action}:{product_id}",
                )
            ]
        ]
    )


def build_categories_keyboard() -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []

    categories = list(ProductTypeCode)
    for i in range(0, len(categories), 2):
        chunk = categories[i : i + 2]
        rows.append(
            [
                InlineKeyboardButton(
                    text=category.name_ru,
                    callback_data=f"excluded_category:{category.value}",
                )
                for category in chunk
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_category_actions_keyboard(
    *,
    category: ProductTypeCode,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚫 Исключить всю категорию",
                    callback_data=f"excluded_category_add_all:{category.value}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="➖ Вернуть всю категорию",
                    callback_data=f"excluded_category_remove_all:{category.value}",
                )
            ],
        ]
    )


async def _send_products_list(
    *,
    message: Message,
    products: list[Product],
    excluded_ids: set[int],
) -> None:
    if not products:
        await message.answer("Ничего не найдено.")
        return

    await message.answer("Найденные продукты:")

    for product in products:
        is_excluded = product.id in excluded_ids
        status = "🚫 Исключён" if is_excluded else "✅ Доступен"

        await message.answer(
            f"{product.name}\nКатегория: {product.type_code}\nСтатус: {status}",
            reply_markup=build_product_toggle_keyboard(
                product_id=product.id,
                is_excluded=is_excluded,
            ),
        )


def _parse_category_from_callback(data: str) -> ProductTypeCode | None:
    raw_category = data.split(":", maxsplit=1)[1]
    try:
        return ProductTypeCode(raw_category)
    except ValueError:
        return None


@router.message(F.text == "🚫 Исключённые продукты")
async def excluded_products_menu(
    message: Message,
    state: FSMContext,
) -> None:
    await state.clear()
    await message.answer(
        "Раздел исключённых продуктов. Выберите действие:",
        reply_markup=excluded_products_keyboard,
    )


@router.message(F.text == "🔎 Найти по названию")
async def ask_search_query(
    message: Message,
    state: FSMContext,
) -> None:
    await state.set_state(ExcludedProductsForm.waiting_for_search_query)
    await message.answer("Введите часть названия продукта.")


@router.message(ExcludedProductsForm.waiting_for_search_query)
async def search_products_for_exclusion(
    message: Message,
    user: User,
    product_service: ProductsService,
    excluded_products_service: UserExcludedProductsService,
    state: FSMContext,
) -> None:
    query = (message.text or "").strip()

    if len(query) < 2:
        await message.answer("Введите минимум 2 символа.")
        return

    products = await product_service.get(
        filters=ProductFilterDTO(
            query=query,
            marketplace=user.settings.marketplace,
            limit=10,
        )
    )

    excluded_products = await excluded_products_service.get_excluded_products(
        user_id=user.id,
    )
    excluded_ids = {product.id for product in excluded_products}

    await state.clear()

    await _send_products_list(
        message=message,
        products=products,
        excluded_ids=excluded_ids,
    )
    await message.answer(
        "Вы можете продолжить работу с исключёнными продуктами.",
        reply_markup=excluded_products_keyboard,
    )


@router.message(F.text == "📂 Выбрать по категории")
async def choose_category(
    message: Message,
) -> None:
    await message.answer(
        "Выберите категорию:",
        reply_markup=build_categories_keyboard(),
    )


@router.callback_query(F.data.startswith("excluded_category:"))
async def show_products_by_category(
    callback: CallbackQuery,
    user: User,
    product_service: ProductsService,
    excluded_products_service: UserExcludedProductsService,
) -> None:
    await callback.answer()

    data = callback.data
    if not data:
        if callback.message:
            await callback.message.answer("Некорректные данные.")
        return

    category = _parse_category_from_callback(data)
    if category is None:
        if callback.message:
            await callback.message.answer("Некорректная категория.")
        return

    products = await product_service.get(
        filters=ProductFilterDTO(
            category=category,
            marketplace=user.settings.marketplace,
            limit=10,
        )
    )

    excluded_products = await excluded_products_service.get_excluded_products(
        user_id=user.id,
    )
    excluded_ids = {product.id for product in excluded_products}

    if callback.message is not None:
        await callback.message.answer(
            f"Категория: {category.name_ru}",
            reply_markup=build_category_actions_keyboard(category=category),
        )
        await _send_products_list(
            message=callback.message,
            products=products,
            excluded_ids=excluded_ids,
        )


@router.callback_query(F.data.startswith("excluded_category_add_all:"))
async def add_excluded_products_by_category(
    callback: CallbackQuery,
    user: User,
    excluded_products_service: UserExcludedProductsService,
) -> None:
    await callback.answer("Исключаю категорию...")

    data = callback.data
    if not data:
        if callback.message:
            await callback.message.answer("Некорректные данные.")
        return

    category = _parse_category_from_callback(data)
    if category is None:
        if callback.message:
            await callback.message.answer("Некорректная категория.")
        return

    excluded_product_ids = (
        await excluded_products_service.add_excluded_products_by_category(
            user_id=user.id,
            category=category,
            marketplace=user.settings.marketplace,
        )
    )

    count = len(excluded_product_ids)

    if callback.message is not None:
        if count == 0:
            await callback.message.answer(
                f"В категории «{category.name_ru}» не найдено продуктов для исключения."
            )
        else:
            await callback.message.answer(
                f"Исключено продуктов из категории «{category.name_ru}»: {count}."
            )


@router.callback_query(F.data.startswith("excluded_category_remove_all:"))
async def remove_excluded_products_by_category(
    callback: CallbackQuery,
    user: User,
    excluded_products_service: UserExcludedProductsService,
) -> None:
    await callback.answer("Возвращаю категорию...")

    data = callback.data
    if not data:
        return

    raw_category = data.split(":", maxsplit=1)[1]

    try:
        category = ProductTypeCode(raw_category)
    except ValueError:
        if callback.message:
            await callback.message.answer("Некорректная категория.")
        return

    marketplace = user.settings.marketplace

    removed_ids = await excluded_products_service.remove_excluded_products_by_category(
        user_id=user.id,
        category=category,
        marketplace=marketplace,
    )

    count = len(removed_ids)

    if callback.message:
        await callback.message.answer(
            f"Возвращено продуктов из категории «{category.name_ru}»: {count}"
        )


@router.message(F.text == "📋 Мои исключения")
async def my_excluded_products(
    message: Message,
    user: User,
    excluded_products_service: UserExcludedProductsService,
) -> None:
    products = await excluded_products_service.get_excluded_products(
        user_id=user.id,
    )
    excluded_ids = {product.id for product in products}

    if not products:
        await message.answer("У Вас пока нет исключённых продуктов.")
        return

    await _send_products_list(
        message=message,
        products=products,
        excluded_ids=excluded_ids,
    )


@router.callback_query(F.data.startswith("excluded_product:add:"))
async def add_excluded_product(
    callback: CallbackQuery,
    user: User,
    excluded_products_service: UserExcludedProductsService,
) -> None:
    await callback.answer("Добавляю...")

    data = callback.data
    if not data:
        if callback.message:
            await callback.message.answer("Некорректные данные.")
        return

    try:
        product_id = int(data.rsplit(":", maxsplit=1)[1])
    except ValueError:
        if callback.message:
            await callback.message.answer("Некорректный product_id.")
        return

    await excluded_products_service.add_excluded_product(
        user_id=user.id,
        product_id=product_id,
    )

    if callback.message is not None:
        await callback.message.answer("Продукт добавлен в исключённые.")


@router.callback_query(F.data.startswith("excluded_product:remove:"))
async def remove_excluded_product(
    callback: CallbackQuery,
    user: User,
    excluded_products_service: UserExcludedProductsService,
) -> None:
    await callback.answer("Убираю...")

    data = callback.data
    if not data:
        if callback.message:
            await callback.message.answer("Некорректные данные.")
        return

    try:
        product_id = int(data.rsplit(":", maxsplit=1)[1])
    except ValueError:
        if callback.message:
            await callback.message.answer("Некорректный product_id.")
        return

    await excluded_products_service.remove_excluded_product(
        user_id=user.id,
        product_id=product_id,
    )

    if callback.message is not None:
        await callback.message.answer("Продукт удалён из исключённых.")


@router.message(F.text == "⬅️ В профиль")
async def back_to_profile_from_excluded_products(
    message: Message,
    state: FSMContext,
) -> None:
    await state.clear()
    await message.answer(
        "Профиль. Выберите раздел:",
        reply_markup=profile_keyboard,
    )
