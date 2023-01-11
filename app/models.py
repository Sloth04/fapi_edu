# -*- coding: utf-8 -*-
import sqlalchemy
import datetime
from sqlalchemy import Column
from helpers.mixins import MysqlPrimaryKeyMixin, MysqlTimestampsMixin
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, TEXT, DATE, TINYINT, BOOLEAN, ENUM
from app.schemas import Role
from app.database import Base


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


class Writer(Base, MysqlPrimaryKeyMixin, MysqlTimestampsMixin):
    __tablename__ = "writers"

    name = Column("name", VARCHAR(255), nullable=False)
    lastname = Column("lastname", VARCHAR(255), nullable=False)
    born = Column("born", DATE(), nullable=False, default=datetime.date.today(),
                  server_default=sqlalchemy.text('(CURRENT_DATE())'))
    died = Column("died", DATE(), nullable=True)


class User(Base, MysqlPrimaryKeyMixin, MysqlTimestampsMixin):
    __tablename__ = "users"

    username = Column("username", VARCHAR(255), nullable=False, index=True)
    email = Column("email", VARCHAR(255), nullable=False, index=True)
    hashed_password = Column("hashed_password", VARCHAR(255), nullable=False)
    full_name = Column("full_name", VARCHAR(255), nullable=True)
    otp_secret = Column("otp_secret", VARCHAR(255), nullable=False)
    disable = Column("disable", BOOLEAN(), nullable=False, default=False)
    role = Column("role", ENUM(Role))
