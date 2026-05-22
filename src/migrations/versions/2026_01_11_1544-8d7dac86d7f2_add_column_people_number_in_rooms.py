"""add column people_number in rooms

Revision ID: 8d7dac86d7f2
Revises: a6cb3b8fd09f
Create Date: 2026-01-11 15:44:43.098326

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8d7dac86d7f2"
down_revision: Union[str, Sequence[str], None] = "a6cb3b8fd09f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("rooms", sa.Column("people_number", sa.Integer(), nullable=False))


def downgrade() -> None:
    op.drop_column("rooms", "people_number")
