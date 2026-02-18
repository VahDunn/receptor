from receptor.db.models import BaseORM
from sqlalchemy.orm import Mapped, mapped_column
import sqlalchemy as sa


class Menu(BaseORM):
    __tablename__ = "menu"

    user_id: Mapped[int] = mapped_column(sa.BigInteger)
    text: Mapped[str] = mapped_column(sa.String)
    calories_per_day: Mapped[int] = mapped_column(sa.SmallInteger)
