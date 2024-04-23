"""add new column in participation

Revision ID: 2024_04_03_1549
Revises: 6ed374791d11
Create Date: 2024-04-03 15:49:40.901367

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2024_04_03_1549"
down_revision: Union[str, None] = "6ed374791d11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "participation",
        sa.Column(
            "last_updated",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("participation", "last_updated")
    # ### end Alembic commands ###