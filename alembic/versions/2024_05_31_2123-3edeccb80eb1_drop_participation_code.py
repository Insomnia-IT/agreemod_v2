"""drop participation_code

Revision ID: 3edeccb80eb1
Revises: b97198c275b0
Create Date: 2024-05-31 21:23:30.239479

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3edeccb80eb1'
down_revision: Union[str, None] = 'b97198c275b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_badge_participation_code_participation_type', 'badge', type_='foreignkey')
    op.drop_column('badge', 'participation_code')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('badge', sa.Column('participation_code', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.create_foreign_key('fk_badge_participation_code_participation_type', 'badge', 'participation_type', ['participation_code'], ['code'])
    # ### end Alembic commands ###
