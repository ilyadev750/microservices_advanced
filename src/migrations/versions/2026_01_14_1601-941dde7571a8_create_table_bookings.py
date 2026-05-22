"""create table bookings

Revision ID: 941dde7571a8
Revises: 086130d7ca7b
Create Date: 2026-01-14 16:01:05.059735

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "941dde7571a8"
down_revision: Union[str, Sequence[str], None] = "086130d7ca7b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("room_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("date_from", sa.Date(), nullable=False),
        sa.Column("date_to", sa.Date(), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["room_id"],
            ["rooms.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.drop_column("rooms", "people_number")


def downgrade() -> None:
    op.add_column(
        "rooms",
        sa.Column("people_number", sa.INTEGER(), autoincrement=False, nullable=False),
    )
    op.drop_table("bookings")
