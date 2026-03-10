from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from receptor.db.models.base import BaseORM

if TYPE_CHECKING:
    from receptor.db.models.user.user import User


class UserIdentity(BaseORM):
    __tablename__ = "user_identity"

    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    provider: Mapped[str] = mapped_column(sa.String, nullable=False)
    external_id: Mapped[str] = mapped_column(sa.String, nullable=False)

    username: Mapped[str | None] = mapped_column(sa.String, nullable=True)
    raw_meta: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)

    user: Mapped[User] = relationship("User", back_populates="identities")

    __table_args__ = (
        sa.UniqueConstraint(
            "provider",
            "external_id",
            name="uq_user_identity_provider_external_id",
        ),
    )
