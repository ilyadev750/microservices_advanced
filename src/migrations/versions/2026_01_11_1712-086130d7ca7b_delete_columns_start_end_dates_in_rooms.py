"""delete columns start, end dates in rooms

Revision ID: 086130d7ca7b
Revises: 1f52253839cd
Create Date: 2026-01-11 17:12:00.764871

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "086130d7ca7b"
down_revision: Union[str, Sequence[str], None] = "1f52253839cd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("rooms", "start_date")
    op.drop_column("rooms", "end_date")


def downgrade() -> None:
    op.add_column(
        "rooms", sa.Column("end_date", sa.DATE(), autoincrement=False, nullable=False)
    )
    op.add_column(
        "rooms", sa.Column("start_date", sa.DATE(), autoincrement=False, nullable=False)
    )
