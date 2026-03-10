from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from receptor.core.domain.marketplaces import Marketplace
from receptor.db.models.base import Base

if TYPE_CHECKING:
    from receptor.db.models.user.user import User


class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
    )

    kcal_min_per_day: Mapped[int] = mapped_column(
        sa.Integer,
        nullable=False,
        server_default=sa.text("2000"),
    )

    kcal_max_per_day: Mapped[int] = mapped_column(
        sa.Integer,
        nullable=False,
        server_default=sa.text("2500"),
    )

    max_money_rub: Mapped[int] = mapped_column(
        sa.Integer,
        nullable=False,
        server_default=sa.text("10000"),
    )

    weekly_budget_tolerance_rub: Mapped[int] = mapped_column(
        sa.Integer,
        nullable=False,
        server_default=sa.text("1000"),
    )

    region: Mapped[str] = mapped_column(
        sa.String,
        nullable=False,
        server_default=sa.text("'Москва'"),
    )

    marketplace: Mapped[Marketplace] = mapped_column(
        sa.Enum(
            Marketplace,
            name="marketplace_enum",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
        server_default=sa.text("'Перекресток'"),
    )

    notifications_enabled: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        server_default=sa.true(),
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="settings",
    )