"""fix foreign key in badge_directions

Revision ID: da891e1e7ce0
Revises: 3266bc37a54d
Create Date: 2024-05-30 20:57:24.969880

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da891e1e7ce0'
down_revision: Union[str, None] = '3266bc37a54d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_badge_directions_direction_id_direction', 'badge_directions', type_='foreignkey')
    op.create_foreign_key(op.f('fk_badge_directions_direction_id_direction'), 'badge_directions', 'direction', ['direction_id'], ['notion_id'], onupdate='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('fk_badge_directions_direction_id_direction'), 'badge_directions', type_='foreignkey')
    op.create_foreign_key('fk_badge_directions_direction_id_direction', 'badge_directions', 'direction', ['direction_id'], ['id'], onupdate='CASCADE')
    # ### end Alembic commands ###
