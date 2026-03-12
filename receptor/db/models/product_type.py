import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from receptor.db.models.base import Base


class ProductType(Base):
    __tablename__ = "product_type"

    code: Mapped[str] = mapped_column(
        sa.String(32), nullable=False, unique=True, primary_key=True
    )
    name_ru: Mapped[str] = mapped_column(sa.String(128), nullable=False)
