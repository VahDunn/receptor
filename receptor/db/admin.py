import json

from fastapi import FastAPI
from sqladmin import Admin, ModelView

from receptor.db.engine import engine
from receptor.db.models import Menu, MenuProduct, Product, ProductType
from receptor.db.models.user.user import User
from receptor.db.models.user.user_settings import UserSettings
from receptor.db.models.user.user_identity import UserIdentity
from receptor.db.models.user.user_account import (
    UserAccount,
    LedgerEntry,
    AccountPayment,
)


class ProductTypeAdmin(ModelView, model=ProductType):
    column_list = [
        ProductType.code,
        ProductType.name_ru,
    ]
    column_searchable_list = [
        ProductType.code,
        ProductType.name_ru,
    ]
    column_sortable_list = [
        ProductType.code,
        ProductType.name_ru,
    ]
    name = "ProductType"
    name_plural = "ProductTypes"
    icon = "fa-solid fa-list"


class ProductAdmin(ModelView, model=Product):
    column_list = [
        Product.id,
        Product.name,
        Product.type_code,
        Product.unit,
        Product.calories_per_unit,
        Product.price_rub,
        Product.marketplace,
        Product.created_at,
    ]
    column_searchable_list = [
        Product.id,
        Product.name,
        Product.type_code,
        Product.marketplace,
    ]
    column_sortable_list = [
        Product.id,
        Product.name,
        Product.type_code,
        Product.unit,
        Product.calories_per_unit,
        Product.price_rub,
        Product.marketplace,
        Product.created_at,
    ]
    form_excluded_columns = ["created_at", "excluded_by_users"]
    page_size = 50

    name = "Product"
    name_plural = "Products"
    icon = "fa-solid fa-apple"


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.name,
        User.role,
        User.created_at,
        User.account,
        User.settings,
        User.identities,
        User.menus,
        User.excluded_products,
    ]
    column_searchable_list = [
        User.id,
        User.name,
    ]
    column_sortable_list = [
        User.id,
        User.name,
        User.role,
        User.created_at,
    ]

    form_excluded_columns = [
        "created_at",
        "menus",
    ]
    page_size = 50

    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"


class UserSettingsAdmin(ModelView, model=UserSettings):
    column_list = [
        UserSettings.user_id,
        UserSettings.kcal_min_per_day,
        UserSettings.kcal_max_per_day,
        UserSettings.max_money_rub,
        UserSettings.weekly_budget_tolerance_rub,
        UserSettings.city,
        UserSettings.marketplace,
        UserSettings.notifications_enabled,
        UserSettings.user,
    ]
    column_searchable_list = [
        UserSettings.user_id,
        UserSettings.city,
        UserSettings.marketplace,
    ]
    column_sortable_list = [
        UserSettings.user_id,
        UserSettings.kcal_min_per_day,
        UserSettings.kcal_max_per_day,
        UserSettings.max_money_rub,
        UserSettings.weekly_budget_tolerance_rub,
        UserSettings.city,
        UserSettings.marketplace,
        UserSettings.notifications_enabled,
    ]

    name = "UserSettings"
    name_plural = "UserSettings"
    icon = "fa-solid fa-sliders"


class UserIdentityAdmin(ModelView, model=UserIdentity):
    column_list = [
        UserIdentity.id,
        UserIdentity.user_id,
        UserIdentity.provider,
        UserIdentity.external_id,
        UserIdentity.username,
        UserIdentity.raw_meta,
        UserIdentity.created_at,
        UserIdentity.user,
    ]
    column_searchable_list = [
        UserIdentity.id,
        UserIdentity.user_id,
        UserIdentity.provider,
        UserIdentity.external_id,
        UserIdentity.username,
    ]
    column_sortable_list = [
        UserIdentity.id,
        UserIdentity.user_id,
        UserIdentity.provider,
        UserIdentity.external_id,
        UserIdentity.username,
        UserIdentity.created_at,
    ]
    form_excluded_columns = ["created_at"]

    column_formatters = {
        UserIdentity.raw_meta: lambda m, a: (
            json.dumps(m.raw_meta, ensure_ascii=False, indent=2)
            if m.raw_meta is not None else ""
        ),
    }

    name = "UserIdentity"
    name_plural = "UserIdentities"
    icon = "fa-solid fa-id-badge"


class UserAccountAdmin(ModelView, model=UserAccount):
    column_list = [
        UserAccount.id,
        UserAccount.user_id,
        UserAccount.currency,
        UserAccount.balance_minor,
        UserAccount.created_at,
        UserAccount.user,
        UserAccount.entries,
    ]
    column_searchable_list = [
        UserAccount.id,
        UserAccount.user_id,
    ]
    column_sortable_list = [
        UserAccount.id,
        UserAccount.user_id,
        UserAccount.currency,
        UserAccount.balance_minor,
        UserAccount.created_at,
    ]
    form_excluded_columns = ["created_at", "entries"]

    name = "UserAccount"
    name_plural = "UserAccounts"
    icon = "fa-solid fa-wallet"


class LedgerEntryAdmin(ModelView, model=LedgerEntry):
    column_list = [
        LedgerEntry.id,
        LedgerEntry.account_id,
        LedgerEntry.amount_minor,
        LedgerEntry.currency,
        LedgerEntry.entry_type,
        LedgerEntry.operation_key,
        LedgerEntry.meta,
        LedgerEntry.created_at,
        LedgerEntry.account,
    ]
    column_searchable_list = [
        LedgerEntry.id,
        LedgerEntry.account_id,
        LedgerEntry.operation_key,
    ]
    column_sortable_list = [
        LedgerEntry.id,
        LedgerEntry.account_id,
        LedgerEntry.amount_minor,
        LedgerEntry.currency,
        LedgerEntry.entry_type,
        LedgerEntry.created_at,
    ]
    form_excluded_columns = ["created_at"]

    column_formatters = {
        LedgerEntry.meta: lambda m, a: (
            json.dumps(m.meta, ensure_ascii=False, indent=2)
            if m.meta is not None else ""
        ),
    }

    name = "LedgerEntry"
    name_plural = "LedgerEntries"
    icon = "fa-solid fa-money-bill-transfer"


class AccountPaymentAdmin(ModelView, model=AccountPayment):
    column_list = [
        AccountPayment.id,
        AccountPayment.user_id,
        AccountPayment.provider,
        AccountPayment.provider_payment_id,
        AccountPayment.status,
        AccountPayment.amount_minor,
        AccountPayment.currency,
        AccountPayment.idempotency_key,
        AccountPayment.confirmation_url,
        AccountPayment.raw_last_event,
        AccountPayment.created_at,
    ]
    column_searchable_list = [
        AccountPayment.id,
        AccountPayment.user_id,
        AccountPayment.provider,
        AccountPayment.provider_payment_id,
        AccountPayment.idempotency_key,
    ]
    column_sortable_list = [
        AccountPayment.id,
        AccountPayment.user_id,
        AccountPayment.provider,
        AccountPayment.status,
        AccountPayment.amount_minor,
        AccountPayment.currency,
        AccountPayment.created_at,
    ]
    form_excluded_columns = ["created_at"]

    column_formatters = {
        AccountPayment.raw_last_event: lambda m, a: (
            json.dumps(m.raw_last_event, ensure_ascii=False, indent=2)
            if m.raw_last_event is not None else ""
        ),
    }

    name = "AccountPayment"
    name_plural = "AccountPayments"
    icon = "fa-solid fa-credit-card"


class MenuAdmin(ModelView, model=Menu):
    column_list = [
        Menu.id,
        Menu.created_at,
        Menu.user_id,
        Menu.max_money_rub,
        Menu.weekly_budget_tolerance_rub,
        Menu.weekly_cost_estimate_rub,
        Menu.daily_kcal_estimates,
        Menu.meta,
        Menu.calorie_target,
        Menu.menu_structure,
        Menu.products_with_quantities,
    ]
    column_sortable_list = [
        Menu.id,
        Menu.created_at,
        Menu.user_id,
        Menu.max_money_rub,
        Menu.weekly_budget_tolerance_rub,
        Menu.weekly_cost_estimate_rub,
    ]
    column_searchable_list = [
        Menu.id,
        Menu.user_id,
    ]
    form_excluded_columns = ["created_at", "products_with_quantities"]
    page_size = 50

    name = "Menu"
    name_plural = "Menus"
    icon = "fa-solid fa-utensils"

    column_formatters = {
        Menu.meta: lambda m, a: json.dumps(m.meta, ensure_ascii=False, indent=2),
        Menu.calorie_target: lambda m, a: json.dumps(m.calorie_target, ensure_ascii=False, indent=2),
        Menu.menu_structure: lambda m, a: json.dumps(m.menu_structure, ensure_ascii=False, indent=2),
    }


class MenuProductAdmin(ModelView, model=MenuProduct):
    column_list = [
        MenuProduct.id,
        MenuProduct.menu_id,
        MenuProduct.product_id,
        MenuProduct.unit,
        MenuProduct.quantity,
        MenuProduct.created_at,
        MenuProduct.product,
    ]
    column_sortable_list = [
        MenuProduct.id,
        MenuProduct.menu_id,
        MenuProduct.product_id,
        MenuProduct.unit,
        MenuProduct.quantity,
        MenuProduct.created_at,
    ]
    column_searchable_list = [
        MenuProduct.id,
        MenuProduct.menu_id,
        MenuProduct.product_id,
    ]
    form_excluded_columns = ["created_at", "menu", "product"]

    name = "MenuProduct"
    name_plural = "MenuProducts"
    icon = "fa-solid fa-cart-shopping"


def setup_admin(app: FastAPI) -> Admin:
    admin = Admin(app, engine)

    admin.add_view(UserAdmin)
    admin.add_view(UserSettingsAdmin)
    admin.add_view(UserIdentityAdmin)
    admin.add_view(UserAccountAdmin)
    admin.add_view(LedgerEntryAdmin)
    admin.add_view(AccountPaymentAdmin)

    admin.add_view(ProductTypeAdmin)
    admin.add_view(ProductAdmin)
    admin.add_view(MenuAdmin)
    admin.add_view(MenuProductAdmin)

    return admin