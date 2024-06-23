"""change coda_index arrival

Revision ID: 3da67c387d5d
Revises: e15e5fc0a581
Create Date: 2024-06-23 15:12:16.019835

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm, sql


# revision identifiers, used by Alembic.
revision: str = '3da67c387d5d'
down_revision: Union[str, None] = 'e15e5fc0a581'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('arrival', 'coda_index',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=True)
    session = orm.Session(bind=op.get_bind())
    session.execute(sql.text("""TRUNCATE TABLE public.arrival cascade"""))
    session.commit()
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('arrival', 'coda_index',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=True)
    # ### end Alembic commands ###
