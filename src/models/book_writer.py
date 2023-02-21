# -*- coding: utf-8 -*-

from sqlalchemy import Column, ForeignKeyConstraint
from sqlalchemy.dialects.mysql import BIGINT

from helpers.mixins import MysqlPrimaryKeyMixin, MysqlTimestampsMixin
from src.database import Base


class BookWriter(Base, MysqlPrimaryKeyMixin, MysqlTimestampsMixin):
    __tablename__ = "book_writers"

    book_id = Column("book_id", BIGINT(unsigned=True), nullable=False)
    writer_id = Column("writer_id", BIGINT(unsigned=True), nullable=False)

    ForeignKeyConstraint(["book_id"], ["books.id"], name="book_writers_book_id_foreign")
    ForeignKeyConstraint(["writer_id"], ["writers.id"], name="book_writers_writer_id_foreign")
