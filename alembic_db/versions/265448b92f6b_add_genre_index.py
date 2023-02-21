"""add_genre_index

Revision ID: 265448b92f6b
Revises: d4c2a4d78115
Create Date: 2023-02-21 14:00:56.421700

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '265448b92f6b'
down_revision = 'd4c2a4d78115'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(op.f('ix_genres_name'), 'genres', ['name'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_genres_name'), table_name='genres')
