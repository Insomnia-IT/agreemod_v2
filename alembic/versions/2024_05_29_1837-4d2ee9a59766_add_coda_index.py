"""add coda_index

Revision ID: 4d2ee9a59766
Revises: 009801ac8083
Create Date: 2024-05-29 18:37:46.522810

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d2ee9a59766'
down_revision: Union[str, None] = '009801ac8083'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('arrival', sa.Column('coda_index', sa.Integer(), nullable=False))
    op.create_unique_constraint(op.f('uq_arrival_coda_index'), 'arrival', ['coda_index'])
    op.add_column('direction', sa.Column('last_updated', sa.TIMESTAMP(), nullable=True))
    op.add_column('participation', sa.Column('coda_index', sa.Integer(), nullable=False))
    op.create_unique_constraint(op.f('uq_participation_coda_index'), 'participation', ['coda_index'])
    op.add_column('person', sa.Column('last_updated', sa.TIMESTAMP(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('person', 'last_updated')
    op.drop_constraint(op.f('uq_participation_coda_index'), 'participation', type_='unique')
    op.drop_column('participation', 'coda_index')
    op.drop_column('direction', 'last_updated')
    op.drop_constraint(op.f('uq_arrival_coda_index'), 'arrival', type_='unique')
    op.drop_column('arrival', 'coda_index')
    # ### end Alembic commands ###
