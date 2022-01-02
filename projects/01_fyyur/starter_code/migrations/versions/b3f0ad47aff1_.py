"""empty message

Revision ID: b3f0ad47aff1
Revises: 42a61d90cc68
Create Date: 2022-01-02 17:03:13.654419

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b3f0ad47aff1'
down_revision = '42a61d90cc68'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('start_time', sa.DateTime(), nullable=False))
    op.add_column('Show', sa.Column('artist_id', sa.Integer(), nullable=False))
    op.add_column('Show', sa.Column('venue_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'Show', 'Artist', ['artist_id'], ['id'])
    op.create_foreign_key(None, 'Show', 'Venue', ['venue_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'Show', type_='foreignkey')
    op.drop_constraint(None, 'Show', type_='foreignkey')
    op.drop_column('Show', 'venue_id')
    op.drop_column('Show', 'artist_id')
    op.drop_column('Show', 'start_time')
    # ### end Alembic commands ###
