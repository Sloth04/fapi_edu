# -*- coding: utf-8 -*-

from sqlalchemy import Column, ForeignKeyConstraint
from sqlalchemy.dialects.mysql import BIGINT

from helpers.mixins import MysqlPrimaryKeyMixin, MysqlTimestampsMixin
from src.database import Base


class BookGenre(Base, MysqlPrimaryKeyMixin, MysqlTimestampsMixin):
    __tablename__ = "book_genres"

    book_id = Column("book_id", BIGINT(unsigned=True), nullable=False)
    genre_id = Column("genre_id", BIGINT(unsigned=True), nullable=False)

    ForeignKeyConstraint(["book_id"], ["books.id"], name="book_genres_book_id_foreign")
    ForeignKeyConstraint(["genre_id"], ["genres.id"], name="book_genres_genre_id_foreign")
