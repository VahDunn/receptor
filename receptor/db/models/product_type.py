from sqlalchemy.orm import Mapped, mapped_column
import sqlalchemy as sa

from receptor.db.models.base import BaseORM


class ProductType(BaseORM):
    __tablename__ = 'product_type'
    name: Mapped[str] = mapped_column(sa.String, nullable=False)