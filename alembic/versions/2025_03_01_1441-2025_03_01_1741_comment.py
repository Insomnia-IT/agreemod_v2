"""COMMENT

Revision ID: 2025_03_01_1741
Revises: 2025_01_27_1806
Create Date: 2025-03-01 14:41:28.351214

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2025_03_01_1741'
down_revision: Union[str, None] = '2025_01_27_1806'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('participation_role', 'is_lead',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('participation_role', 'is_team',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('participation_role', 'color',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('participation_role', 'notion_id',
               existing_type=sa.UUID(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('participation_role', 'notion_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.alter_column('participation_role', 'color',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('participation_role', 'is_team',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.alter_column('participation_role', 'is_lead',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    # ### end Alembic commands ###
