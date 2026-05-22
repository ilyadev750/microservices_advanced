"""create table rooms

Revision ID: cebf6de77685
Revises: d15ef5ec81b4
Create Date: 2025-12-15 13:22:54.941033

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "cebf6de77685"
down_revision: Union[str, Sequence[str], None] = "d15ef5ec81b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rooms",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("hotel_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["hotel_id"],
            ["hotels.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("rooms")
