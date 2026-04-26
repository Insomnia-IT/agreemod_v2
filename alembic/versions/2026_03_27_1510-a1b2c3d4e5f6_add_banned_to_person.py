"""Add banned boolean field to person

Revision ID: a1b2c3d4e5f6
Revises: 969a79ceae2f
Create Date: 2026-03-27 15:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '969a79ceae2f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('person', sa.Column('banned', sa.Boolean(), nullable=True, server_default='false'))


def downgrade() -> None:
    op.drop_column('person', 'banned')