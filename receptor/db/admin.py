from fastapi import FastAPI
from sqladmin import Admin, ModelView

from receptor.db.engine import engine
from receptor.db.models import Menu, MenuProduct, Product, ProductType


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
        Product.created_at,
    ]
    column_searchable_list = [
        Product.name,
        Product.type_code,
        Product.id,
    ]
    column_sortable_list = [
        Product.id,
        Product.name,
        Product.type_code,
        Product.unit,
        Product.calories_per_unit,
        Product.price_rub,
        Product.created_at,
    ]
    form_excluded_columns = ["created_at"]
    name = "Product"
    name_plural = "Products"
    icon = "fa-solid fa-apple"


class MenuAdmin(ModelView, model=Menu):
    column_list = [
        Menu.id,
        Menu.created_at,
        Menu.user_id,
        Menu.daily_kcal_estimates,
        Menu.meta,
        Menu.calorie_target,
        Menu.menu_structure,
        Menu.products_with_quantities,
    ]
    column_list = [c for c in column_list if c is not None]

    column_sortable_list = [Menu.id, Menu.created_at, Menu.user_id]
    column_sortable_list = [c for c in column_sortable_list if c is not None]

    column_searchable_list = [
        Menu.user_id,
        Menu.id,
    ]
    column_searchable_list = [c for c in column_searchable_list if c is not None]

    form_excluded_columns = ["created_at", "products_with_quantities"]

    name = "Menu"
    name_plural = "Menus"
    icon = "fa-solid fa-utensils"


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
        MenuProduct.menu_id,
        MenuProduct.product_id,
        MenuProduct.id,
    ]
    form_excluded_columns = ["created_at", "menu", "product"]

    name = "MenuProduct"
    name_plural = "MenuProducts"
    icon = "fa-solid fa-cart-shopping"


def setup_admin(app: FastAPI) -> Admin:
    admin = Admin(app, engine)

    admin.add_view(ProductTypeAdmin)
    admin.add_view(ProductAdmin)
    admin.add_view(MenuAdmin)
    admin.add_view(MenuProductAdmin)

    return admin
