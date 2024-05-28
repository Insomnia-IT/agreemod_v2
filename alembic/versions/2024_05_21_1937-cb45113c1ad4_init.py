"""init

Revision ID: cb45113c1ad4
Revises: 
Create Date: 2024-05-21 19:37:24.179981

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'cb45113c1ad4'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('badge_color',
    sa.Column('code', sa.String(), nullable=False),
    sa.Column('color', sa.String(), nullable=False),
    sa.Column('comment', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('code', name=op.f('pk_badge_color'))
    )
    op.create_table('direction_type',
    sa.Column('code', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('is_federal', sa.Boolean(), nullable=False),
    sa.Column('comment', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('code', name=op.f('pk_direction_type'))
    )
    op.create_table('participation_role',
    sa.Column('code', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('is_lead', sa.Boolean(), nullable=False),
    sa.Column('is_team', sa.Boolean(), nullable=False),
    sa.Column('is_free_feed', sa.Boolean(), nullable=True),
    sa.Column('comment', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('code', name=op.f('pk_participation_role'))
    )
    op.create_table('participation_status',
    sa.Column('code', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('to_list', sa.Boolean(), nullable=False),
    sa.Column('comment', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('code', name=op.f('pk_participation_status'))
    )
    op.create_table('person',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=True),
    sa.Column('first_name', sa.String(), nullable=True),
    sa.Column('nickname', sa.String(), nullable=True),
    sa.Column('other_names', sa.ARRAY(sa.String()), nullable=True),
    sa.Column('gender', sa.String(), nullable=True),
    sa.Column('birth_date', sa.Date(), nullable=True),
    sa.Column('city', sa.String(), nullable=True),
    sa.Column('telegram', sa.String(), nullable=True),
    sa.Column('phone', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('diet', sa.String(), nullable=True),
    sa.Column('comment', sa.String(), nullable=True),
    sa.Column('notion_id', sa.UUID(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_person')),
    sa.UniqueConstraint('notion_id', name=op.f('uq_person_notion_id'))
    )
    op.create_table('transport_type',
    sa.Column('code', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('comment', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('code', name=op.f('pk_transport_type'))
    )
    op.create_table('direction',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('first_year', sa.Integer(), nullable=True),
    sa.Column('last_year', sa.Integer(), nullable=True),
    sa.Column('notion_id', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['type'], ['direction_type.code'], name=op.f('fk_direction_type_direction_type')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_direction')),
    sa.UniqueConstraint('notion_id', name=op.f('uq_direction_notion_id'))
    )
    op.create_table('participation_type',
    sa.Column('code', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('badge_color', sa.String(), nullable=True),
    sa.Column('comment', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['badge_color'], ['badge_color.code'], name=op.f('fk_participation_type_badge_color_badge_color')),
    sa.PrimaryKeyConstraint('code', name=op.f('pk_participation_type'))
    )
    op.create_table('badge',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=True),
    sa.Column('first_name', sa.String(), nullable=True),
    sa.Column('nickname', sa.String(), nullable=True),
    sa.Column('gender', sa.String(), nullable=True),
    sa.Column('phone', sa.String(), nullable=True),
    sa.Column('infant_id', sa.UUID(), nullable=True),
    sa.Column('diet', sa.String(), nullable=True),
    sa.Column('feed', sa.String(), nullable=True),
    sa.Column('number', sa.String(), nullable=False),
    sa.Column('batch', sa.Integer(), nullable=False),
    sa.Column('participation_code', sa.String(), nullable=False),
    sa.Column('role_code', sa.String(), nullable=True),
    sa.Column('photo', sa.String(), nullable=True),
    sa.Column('person_id', sa.UUID(), nullable=True),
    sa.Column('comment', sa.String(), nullable=True),
    sa.Column('notion_id', sa.UUID(), nullable=True),
    sa.Column('last_updated', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['infant_id'], ['badge.id'], name=op.f('fk_badge_infant_id_badge')),
    sa.ForeignKeyConstraint(['participation_code'], ['participation_type.code'], name=op.f('fk_badge_participation_code_participation_type')),
    sa.ForeignKeyConstraint(['person_id'], ['person.id'], name=op.f('fk_badge_person_id_person')),
    sa.ForeignKeyConstraint(['role_code'], ['participation_role.code'], name=op.f('fk_badge_role_code_participation_role')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_badge')),
    sa.UniqueConstraint('notion_id', name=op.f('uq_badge_notion_id')),
    sa.UniqueConstraint('number', name=op.f('uq_badge_number'))
    )
    op.create_table('participation',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('person_id', sa.UUID(), nullable=False),
    sa.Column('direction_id', sa.UUID(), nullable=False),
    sa.Column('role_code', sa.String(), nullable=True),
    sa.Column('participation_code', sa.String(), nullable=False),
    sa.Column('status_code', sa.String(), nullable=False),
    sa.Column('notion_id', sa.UUID(), nullable=True),
    sa.Column('last_updated', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['direction_id'], ['direction.id'], name=op.f('fk_participation_direction_id_direction')),
    sa.ForeignKeyConstraint(['participation_code'], ['participation_type.code'], name=op.f('fk_participation_participation_code_participation_type')),
    sa.ForeignKeyConstraint(['person_id'], ['person.id'], name=op.f('fk_participation_person_id_person')),
    sa.ForeignKeyConstraint(['role_code'], ['participation_role.code'], name=op.f('fk_participation_role_code_participation_role')),
    sa.ForeignKeyConstraint(['status_code'], ['participation_status.code'], name=op.f('fk_participation_status_code_participation_status')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_participation')),
    sa.UniqueConstraint('notion_id', name=op.f('uq_participation_notion_id'))
    )
    op.create_table('arrival',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('badge_id', sa.UUID(), nullable=False),
    sa.Column('arrival_date', sa.Date(), nullable=False),
    sa.Column('arrival_transport', sa.String(), nullable=True),
    sa.Column('arrival_registered', sa.TIMESTAMP(), nullable=True),
    sa.Column('departure_date', sa.Date(), nullable=False),
    sa.Column('departure_transport', sa.String(), nullable=True),
    sa.Column('departure_registered', sa.TIMESTAMP(), nullable=True),
    sa.Column('extra_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('comment', sa.String(), nullable=True),
    sa.Column('last_updated', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['badge_id'], ['badge.id'], name=op.f('fk_arrival_badge_id_badge')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_arrival'))
    )
    op.create_table('badge_directions',
    sa.Column('badge_id', sa.UUID(), nullable=False),
    sa.Column('direction_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['badge_id'], ['badge.id'], name=op.f('fk_badge_directions_badge_id_badge'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['direction_id'], ['direction.id'], name=op.f('fk_badge_directions_direction_id_direction'), onupdate='CASCADE'),
    sa.PrimaryKeyConstraint('badge_id', 'direction_id', name=op.f('pk_badge_directions'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('badge_directions')
    op.drop_table('arrival')
    op.drop_table('participation')
    op.drop_table('badge')
    op.drop_table('participation_type')
    op.drop_table('direction')
    op.drop_table('transport_type')
    op.drop_table('person')
    op.drop_table('participation_status')
    op.drop_table('participation_role')
    op.drop_table('direction_type')
    op.drop_table('badge_color')
    # ### end Alembic commands ###