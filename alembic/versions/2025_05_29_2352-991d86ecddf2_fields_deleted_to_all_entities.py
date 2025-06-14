"""Fields deleted to all entities

Revision ID: 991d86ecddf2
Revises: 2025_03_27_0006
Create Date: 2025-05-29 23:52:02.050231

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '991d86ecddf2'
down_revision: Union[str, None] = '2025_03_27_0006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('arrival', sa.Column('deleted', sa.Boolean(), nullable=True))
    op.add_column('badge', sa.Column('deleted', sa.Boolean(), nullable=True))
    op.add_column('direction', sa.Column('deleted', sa.Boolean(), nullable=True))
    op.add_column('participation', sa.Column('deleted', sa.Boolean(), nullable=True))
    op.add_column('person', sa.Column('deleted', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('person', 'deleted')
    op.drop_column('participation', 'deleted')
    op.drop_column('direction', 'deleted')
    op.drop_column('badge', 'deleted')
    op.drop_column('arrival', 'deleted')
    # ### end Alembic commands ###