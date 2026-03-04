from typing import TYPE_CHECKING

from receptor.db.models.base import Base
import sqlalchemy as sa
from sqlalchemy.orm import relationship, Mapped, mapped_column

if TYPE_CHECKING:
    from receptor.db.models.user import User


class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
    )

    kcal_min_per_day: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    kcal_max_per_day: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)

    max_money_rub: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    weekly_budget_tolerance_rub: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)

    city: Mapped[str | None] = mapped_column(sa.String, nullable=True)
    marketplace: Mapped[str | None] = mapped_column(sa.String, nullable=True)

    notifications_enabled: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        server_default=sa.true(),
    )

    user: Mapped["User"] = relationship("User", back_populates="settings")