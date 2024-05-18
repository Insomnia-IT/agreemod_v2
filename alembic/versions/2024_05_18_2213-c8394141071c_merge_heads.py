"""empty message

Revision ID: c8394141071c
Revises: 2024_04_03_1604, 2024_04_06_1925
Create Date: 2024-05-18 22:13:22.244722

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c8394141071c"
down_revision: Union[str, None] = ("2024_04_03_1604", "2024_04_06_1925")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
