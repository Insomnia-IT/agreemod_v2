"""add status to arrival, all anonymous badges table

Revision ID: 081e327b9a8a
Revises: bf93aaff0bfa
Create Date: 2024-06-11 17:56:10.700466

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm

from updater.src.db.orm.dictionaries_orm import TransportTypeAppORM

# revision identifiers, used by Alembic.
revision: str = '081e327b9a8a'
down_revision: Union[str, None] = 'bf93aaff0bfa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    session = orm.Session(bind=op.get_bind())
    session.add_all(TransportTypeAppORM.fill_table())
    session.commit()

    op.create_table('anonymous_badges',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('subtitle', sa.String(), nullable=True),
    sa.Column('batch', sa.String(), nullable=True),
    sa.Column('color', sa.String(), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('to_print', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['color'], ['badge_color.code'], name=op.f('fk_anonymous_badges_color_badge_color')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_anonymous_badges'))
    )
    op.add_column('arrival', sa.Column('status', sa.String(), nullable=True))
    op.create_foreign_key(op.f('fk_arrival_departure_transport_transport_type'), 'arrival', 'transport_type', ['departure_transport'], ['code'])
    op.create_foreign_key(op.f('fk_arrival_arrival_transport_transport_type'), 'arrival', 'transport_type', ['arrival_transport'], ['code'])
    op.create_foreign_key(op.f('fk_arrival_status_participation_status'), 'arrival', 'participation_status', ['status'], ['code'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('fk_arrival_status_participation_status'), 'arrival', type_='foreignkey')
    op.drop_constraint(op.f('fk_arrival_arrival_transport_transport_type'), 'arrival', type_='foreignkey')
    op.drop_constraint(op.f('fk_arrival_departure_transport_transport_type'), 'arrival', type_='foreignkey')
    op.drop_column('arrival', 'status')
    op.drop_table('anonymous_badges')
    # ### end Alembic commands ###
