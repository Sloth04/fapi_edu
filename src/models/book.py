# -*- coding: utf-8 -*-
import datetime

import sqlalchemy
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, TEXT, DATE, TINYINT

from helpers.mixins import MysqlPrimaryKeyMixin, MysqlTimestampsMixin
from src.database import Base


class Book(Base, MysqlPrimaryKeyMixin, MysqlTimestampsMixin):
    __tablename__ = "books"

    title = Column("title", VARCHAR(255), nullable=False)
    writer_id = Column("writer_id", BIGINT(unsigned=True), nullable=False)
    description = Column("description", TEXT(), nullable=True)
    publish_date = Column("publish_date", DATE(), default=datetime.date.today(),
                          server_default=sqlalchemy.text('(CURRENT_DATE())'))
    rating = Column("rating", TINYINT(unsigned=True), nullable=True)
    cover_file = Column("cover_file", VARCHAR(255), nullable=True)
    book_file = Column("book_file", VARCHAR(255), nullable=True)
    genres = Column("genres", TEXT(), nullable=True)
