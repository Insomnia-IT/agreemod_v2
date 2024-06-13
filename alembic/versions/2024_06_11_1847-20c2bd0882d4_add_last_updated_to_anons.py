"""add last updated to anons

Revision ID: 20c2bd0882d4
Revises: 5661c2563d6a
Create Date: 2024-06-11 18:47:23.300780

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20c2bd0882d4'
down_revision: Union[str, None] = '5661c2563d6a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('anonymous_badges', sa.Column('last_updated', sa.TIMESTAMP(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('anonymous_badges', 'last_updated')
    # ### end Alembic commands ###