"""add_indexes

Revision ID: fbd02f8a2927
Revises: c9b65af3b3fc
Create Date: 2023-02-07 15:22:23.789967

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fbd02f8a2927'
down_revision = 'c9b65af3b3fc'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(op.f('ix_writers_name_lastname_born'), 'writers', ['name', 'lastname', 'born'], unique=True)
    op.create_index(op.f('ix_books_title_writer_id'), 'books', ['title', 'writer_id'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_writers_name_lastname_born'), table_name='writers')
    op.drop_index(op.f('ix_books_title_writer_id'), table_name='books')
