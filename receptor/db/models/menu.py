from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from receptor.db.models.base import BaseORM

if TYPE_CHECKING:
    from receptor.db.models import Product


class Menu(BaseORM):
    __tablename__ = "menu"

    user_id: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False)
    calorie_target: Mapped[dict] = mapped_column(JSONB, nullable=False)

    menu_structure: Mapped[list[dict]] = mapped_column(JSONB, nullable=False)

    daily_kcal_estimates: Mapped[list[int]] = mapped_column(
        sa.ARRAY(sa.Integer),
        nullable=False,
    )

    products_with_quantities: Mapped[list["MenuProduct"]] = relationship(
        "MenuProduct",
        back_populates="menu",
        cascade="all, delete-orphan",
    )


class MenuProduct(BaseORM):
    __tablename__ = "menu_product"

    menu_id: Mapped[int] = mapped_column(
        sa.ForeignKey("menu.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    product_id: Mapped[int] = mapped_column(
        sa.ForeignKey("product.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )

    unit: Mapped[str] = mapped_column(sa.String(8), nullable=False)

    quantity: Mapped[Decimal] = mapped_column(sa.Numeric(10, 3), nullable=False)

    menu: Mapped["Menu"] = relationship(
        "Menu", back_populates="products_with_quantities"
    )
    product: Mapped["Product"] = relationship("Product")

    __table_args__ = (
        sa.UniqueConstraint("menu_id", "product_id", name="uq_menu_product"),
        sa.CheckConstraint("quantity > 0", name="ck_menu_product_quantity_gt_0"),
    )
