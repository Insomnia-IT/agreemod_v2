"""drop participation_type

Revision ID: bf93aaff0bfa
Revises: 9874654430d5
Create Date: 2024-06-03 18:37:41.958890

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bf93aaff0bfa'
down_revision: Union[str, None] = '9874654430d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('participation_type')
    op.drop_constraint('fk_participation_participation_code_participation_type', 'participation', type_='foreignkey')
    op.drop_column('participation', 'participation_code')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('participation', sa.Column('participation_code', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.create_foreign_key('fk_participation_participation_code_participation_type', 'participation', 'participation_type', ['participation_code'], ['code'])
    op.create_table('participation_type',
    sa.Column('code', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('badge_color', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('comment', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['badge_color'], ['badge_color.code'], name='fk_participation_type_badge_color_badge_color'),
    sa.PrimaryKeyConstraint('code', name='pk_participation_type')
    )
    # ### end Alembic commands ###