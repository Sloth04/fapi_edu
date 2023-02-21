"""add_book_writers_table

Revision ID: d4c2a4d78115
Revises: 7e82132f7d4a
Create Date: 2023-02-21 11:02:22.360238

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'd4c2a4d78115'
down_revision = '7e82132f7d4a'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('books', 'writer_id')
    op.create_table('book_writers',
                    sa.Column('id', mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False),
                    sa.Column('book_id', mysql.BIGINT(unsigned=True), nullable=False),
                    sa.Column('writer_id', mysql.BIGINT(unsigned=True), nullable=False),
                    sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'),
                              nullable=False),
                    sa.Column('updated_at', mysql.TIMESTAMP(),
                              server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_book_writers_updated_at'), 'book_writers', ['updated_at'], unique=False)
    op.create_foreign_key(
        op.f("book_writers_book_id_foreign"), "book_writers", "books", ["book_id"], ["id"]
    )
    op.create_foreign_key(
        op.f("book_writers_writer_id_foreign"), "book_writers", "writers", ["writer_id"], ["id"]
    )


def downgrade():
    op.drop_index(op.f('ix_book_writers_updated_at'), table_name='book_writers')
    op.drop_constraint(
        op.f("book_writers_book_id_foreign"), type_="foreignkey", table_name="book_writers"
    )
    op.drop_constraint(
        op.f("book_writers_writer_id_foreign"), type_="foreignkey", table_name="book_writers"
    )
    op.drop_table('book_writers')
