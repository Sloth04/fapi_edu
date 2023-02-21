"""add_book_genres_table

Revision ID: 7e82132f7d4a
Revises: 371691e7b10f
Create Date: 2023-02-21 11:02:09.490246

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '7e82132f7d4a'
down_revision = '371691e7b10f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('book_genres',
                    sa.Column('id', mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False),
                    sa.Column('book_id', mysql.BIGINT(unsigned=True), nullable=False),
                    sa.Column('genre_id', mysql.BIGINT(unsigned=True), nullable=False),
                    sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'),
                              nullable=False),
                    sa.Column('updated_at', mysql.TIMESTAMP(),
                              server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_book_genres_updated_at'), 'book_genres', ['updated_at'], unique=False)
    op.create_foreign_key(
        op.f("book_genres_book_id_foreign"), "book_genres", "books", ["book_id"], ["id"]
    )
    op.create_foreign_key(
        op.f("book_genres_genre_id_foreign"), "book_genres", "genres", ["genre_id"], ["id"]
    )


def downgrade():
    op.drop_index(op.f('ix_book_genres_updated_at'), table_name='book_genres')
    op.drop_constraint(
        op.f("book_genres_book_id_foreign"), type_="foreignkey", table_name="book_genres"
    )
    op.drop_constraint(
        op.f("book_genres_genre_id_foreign"), type_="foreignkey", table_name="book_genres"
    )
    op.drop_table('book_genres')
