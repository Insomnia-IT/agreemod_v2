"""populate_dicts

Revision ID: 5e144e40c20d
Revises: cb45113c1ad4
Create Date: 2024-05-21 19:38:53.467610

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import orm

from alembic import op
from updater.src.db.orm.dictionaries_orm import (
    BadgeColorAppORM,
    DirectionTypeAppORM,
)

# revision identifiers, used by Alembic.
revision: str = '5e144e40c20d'
down_revision: Union[str, None] = 'cb45113c1ad4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    session = orm.Session(bind=op.get_bind())
    session.add_all(BadgeColorAppORM.fill_table())
    session.add_all(DirectionTypeAppORM.fill_table())
    session.commit()
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
