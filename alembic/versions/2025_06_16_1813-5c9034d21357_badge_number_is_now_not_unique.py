"""Badge_number is now not unique

Revision ID: 5c9034d21357
Revises: 8d70087016ed
Create Date: 2025-06-16 18:13:52.575896

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c9034d21357'
down_revision: Union[str, None] = '8d70087016ed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('uq_badge_number', 'badge', type_='unique')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('uq_badge_number', 'badge', ['number'])
    # ### end Alembic commands ###