from sqlalchemy.orm import Mapped, relationship, mapped_column
import sqlalchemy as sa

from receptor.db.models.product_type import ProductType
from receptor.db.models.base import BaseORM


class Product(BaseORM):
    __tablename__ = "product"
    name: Mapped[str] = mapped_column(sa.String)
    type_code: Mapped[str] = mapped_column(
        sa.ForeignKey("product_type.code", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type: Mapped[ProductType] = relationship("ProductType")
    unit: Mapped[str] = mapped_column(sa.String)
    calories_per_unit: Mapped[int] = mapped_column(sa.SmallInteger)
    price_rub: Mapped[int]
