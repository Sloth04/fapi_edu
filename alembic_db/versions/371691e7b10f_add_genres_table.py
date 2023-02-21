"""add_genres_table

Revision ID: 371691e7b10f
Revises: fbd02f8a2927
Create Date: 2023-02-21 11:01:49.625944

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '371691e7b10f'
down_revision = 'fbd02f8a2927'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('books', 'genres')
    op.create_table('genres',
                    sa.Column('id', mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False),
                    sa.Column('title', mysql.VARCHAR(length=255), nullable=False),
                    sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'),
                              nullable=False),
                    sa.Column('updated_at', mysql.TIMESTAMP(),
                              server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_genres_updated_at'), 'genres', ['updated_at'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_genres_updated_at'), table_name='genres')
    op.drop_table('genres')
    op.execute(
        "ALTER TABLE `books` "
        "ADD COLUMN `genres` TEXT NULL AFTER `book_file`;"
    )
