"""unique email

Revision ID: a6cb3b8fd09f
Revises: cc16a3efed79
Create Date: 2025-12-26 14:15:21.259814

"""

# ruff: noqa: F401
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a6cb3b8fd09f"
down_revision: Union[str, Sequence[str], None] = "cc16a3efed79"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(None, "users", ["email"])


def downgrade() -> None:
    op.drop_constraint(None, "users", type_="unique")
