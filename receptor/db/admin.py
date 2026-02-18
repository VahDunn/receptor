from fastapi import FastAPI
from sqladmin import Admin, ModelView

from receptor.db.engine import engine
from receptor.db.models import Product, ProductType


class ProductTypeAdmin(ModelView, model=ProductType):
    column_list = [
        ProductType.name_ru,
        ProductType.code,
    ]
    column_searchable_list = [
        ProductType.name_ru,
        ProductType.code,
    ]
    name = "ProductType"
    name_plural = "ProductTypes"
    icon = "fa-solid fa-list"


class ProductAdmin(ModelView, model=Product):
    column_list = [
        Product.id,
        Product.name,
        Product.type_code,
        Product.type,
        Product.unit,
        Product.calories_per_unit,
        Product.created_at,
        Product.price_rub,
    ]
    column_searchable_list = [
        Product.name,
        Product.type,
        Product.id,
    ]
    form_excluded_columns = ["created_at"]
    name = "Product"
    name_plural = "Products"
    icon = "fa-solid fa-apple"


def setup_admin(app: FastAPI) -> Admin:
    admin = Admin(app, engine)
    admin.add_view(ProductTypeAdmin)
    admin.add_view(ProductAdmin)
    return admin
