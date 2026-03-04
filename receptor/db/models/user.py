from typing import TYPE_CHECKING
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, relationship, mapped_column

from receptor.db.models.base import BaseORM
from receptor.db.models.user_product import user_excluded_product

if TYPE_CHECKING:
    from receptor.db.models.menu import Menu
    from receptor.db.models.product import Product
    from receptor.db.models.user_settings import UserSettings

class User(BaseORM):
    __tablename__ = "user"
    name: Mapped[str] = mapped_column(sa.String, nullable=False)

    settings: Mapped["UserSettings"] = relationship(
        "UserSettings",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    menus: Mapped[list["Menu"]] = relationship(
        "Menu",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    excluded_products: Mapped[list["Product"]] = relationship(
        "Product",
        secondary=user_excluded_product,
        back_populates="excluded_by_users",
    )



