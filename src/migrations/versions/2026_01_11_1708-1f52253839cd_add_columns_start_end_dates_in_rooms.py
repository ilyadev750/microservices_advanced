"""add columns start, end dates in rooms

Revision ID: 1f52253839cd
Revises: 8d7dac86d7f2
Create Date: 2026-01-11 17:08:07.969956

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1f52253839cd"
down_revision: Union[str, Sequence[str], None] = "8d7dac86d7f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("rooms", sa.Column("start_date", sa.Date(), nullable=False))
    op.add_column("rooms", sa.Column("end_date", sa.Date(), nullable=False))


def downgrade() -> None:
    op.drop_column("rooms", "end_date")
    op.drop_column("rooms", "start_date")
