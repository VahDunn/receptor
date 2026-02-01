from sqlalchemy.orm import Mapped
import sqlalchemy as sa
from receptor.db.models.base import BaseORM


class Product(BaseORM):
    __tablename__ = "product"
    name: Mapped[str] = sa.Column(sa.String)
    type: Mapped[int] # тут будет связь на справочник типов
    measure_unit: Mapped[str] # тут тоже, на справочник единиц измерения
    calories_per_unit: Mapped[int]
    price_rub: Mapped[int]