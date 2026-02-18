import sqlalchemy as sa
from receptor.db.models import BaseORM
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ARRAY

from receptor.db.models.menu import Menu


class User(BaseORM):
    __tablename__ = "user"

    menus: Mapped[Menu] = relationship()
    excluded_products_ids: Mapped[int] = mapped_column(ARRAY(sa.BigInteger))
    excluded_products: Mapped[Menu] = (
        relationship()
    )  # TODO будет таблица n-n для  пользователей и исключенных ими продуктов
