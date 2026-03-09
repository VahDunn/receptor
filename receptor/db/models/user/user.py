from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from receptor.core.domain.user_roles import UserRole
from receptor.db.models.base import BaseORM

if TYPE_CHECKING:
    from receptor.db.models.menu import Menu
    from receptor.db.models.product import Product
    from receptor.db.models.user.user_account import UserAccount
    from receptor.db.models.user.user_identity import UserIdentity
    from receptor.db.models.user.user_settings import UserSettings


user_excluded_product = sa.Table(
    "user_excluded_product",
    BaseORM.metadata,
    sa.Column(
        "user_id",
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    sa.Column(
        "product_id",
        sa.ForeignKey("product.id", ondelete="RESTRICT"),
        primary_key=True,
    ),
    sa.Index("ix_user_excluded_product_user_id", "user_id"),
    sa.Index("ix_user_excluded_product_product_id", "product_id"),
)


class User(BaseORM):
    __tablename__ = "user"

    name: Mapped[str] = mapped_column(sa.String, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(
        sa.String(1023),
        nullable=True,
    )

    role: Mapped[UserRole] = mapped_column(
        sa.Enum(
            UserRole,
            name="user_role",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
        server_default=sa.text("'USER'"),
    )

    account: Mapped["UserAccount"] = relationship(
        "UserAccount",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    identities: Mapped[list["UserIdentity"]] = relationship(
        "UserIdentity",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    settings: Mapped["UserSettings"] = relationship(
        "UserSettings",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    menus: Mapped[list["Menu"]] = relationship(
        "Menu",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    excluded_products: Mapped[list["Product"]] = relationship(
        "Product",
        secondary=user_excluded_product,
        back_populates="excluded_by_users",
    )

    def __str__(self) -> str:
        return f"{self.id} | {self.name}"

    def __repr__(self) -> str:
        return f"User(id={self.id}, name='{self.name}')"