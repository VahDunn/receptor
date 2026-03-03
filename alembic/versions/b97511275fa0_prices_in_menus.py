"""prices_in_menus

Revision ID: b97511275fa0
Revises: 18629b035c2e
Create Date: 2026-03-03 11:59:15.784708

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b97511275fa0"
down_revision: Union[str, Sequence[str], None] = "18629b035c2e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "menu",
        sa.Column(
            "max_money_rub",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("10000"),
        ),
    )
    op.add_column(
        "menu",
        sa.Column(
            "weekly_budget_tolerance_rub",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("500"),
        ),
    )
    op.add_column(
        "menu",
        sa.Column(
            "weekly_cost_estimate_rub",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )

    op.alter_column("menu", "max_money_rub", server_default=None)
    op.alter_column("menu", "weekly_budget_tolerance_rub", server_default=None)
    op.alter_column("menu", "weekly_cost_estimate_rub", server_default=None)


def downgrade() -> None:
    op.drop_column("menu", "weekly_cost_estimate_rub")
    op.drop_column("menu", "weekly_budget_tolerance_rub")
    op.drop_column("menu", "max_money_rub")