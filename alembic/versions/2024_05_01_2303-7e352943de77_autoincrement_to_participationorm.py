"""autoincrement to ParticipationORM

Revision ID: 7e352943de77
Revises: 2024_04_03_1604
Create Date: 2024-05-01 23:03:15.491679

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7e352943de77'
down_revision: Union[str, None] = '2024_04_03_1604'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

tablename = "participation"
column_name = "id"


def upgrade():
    op.execute(f"CREATE SEQUENCE IF NOT EXISTS {tablename}_{column_name}_seq CASCADE")
    op.execute(f"ALTER TABLE {tablename} ALTER COLUMN {column_name} SET DEFAULT nextval('{tablename}_{column_name}_seq')")


# Downgrade function
def downgrade():
    op.execute(f"DROP SEQUENCE IF EXISTS {tablename}_{column_name}_seq")
    op.execute(f"ALTER TABLE {tablename} ALTER COLUMN {column_name} DROP DEFAULT")