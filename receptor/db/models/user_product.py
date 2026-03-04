import sqlalchemy as sa
from receptor.db.models.base import BaseORM

user_excluded_product = sa.Table(
    "user_excluded_product",
    BaseORM.metadata,
    sa.Column(
        "user_id",
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,   # можно так, тогда UniqueConstraint не нужен
    ),
    sa.Column(
        "product_id",
        sa.ForeignKey("product.id", ondelete="RESTRICT"),
        primary_key=True,
    ),
    sa.Index("ix_user_excluded_product_user_id", "user_id"),
    sa.Index("ix_user_excluded_product_product_id", "product_id"),
)