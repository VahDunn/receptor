from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship, mapped_column
import sqlalchemy as sa

from receptor.core.domain.units import Unit
from receptor.db.models.product_type import ProductType
from receptor.db.models.base import BaseORM
from receptor.db.models.user.user_product import user_excluded_product

if TYPE_CHECKING:
    from receptor.db.models.user.user import User

class Product(BaseORM):
    __tablename__ = "product"
    name: Mapped[str] = mapped_column(sa.String)
    type_code: Mapped[str] = mapped_column(
        sa.ForeignKey("product_type.code", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type: Mapped[ProductType] = relationship("ProductType")
    unit: Mapped[str] = mapped_column(sa.String, nullable=False)
    calories_per_unit: Mapped[int] = mapped_column(sa.SmallInteger)
    price_rub: Mapped[int]
    marketplace: Mapped[str] = mapped_column(sa.String, nullable=False)

    excluded_by_users: Mapped[list["User"]] = relationship(
        "User",
        secondary=user_excluded_product,
        back_populates="excluded_products",
    )

    __table_args__ = (
        sa.CheckConstraint(
            f"unit IN ({', '.join(repr(u.value) for u in Unit)})",
            name="ck_product_unit_valid",
        ),
    )
