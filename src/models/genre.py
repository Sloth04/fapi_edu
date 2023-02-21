# -*- coding: utf-8 -*-

from sqlalchemy import Column
from sqlalchemy.dialects.mysql import VARCHAR

from helpers.mixins import MysqlPrimaryKeyMixin, MysqlTimestampsMixin
from src.database import Base


class Genre(Base, MysqlPrimaryKeyMixin, MysqlTimestampsMixin):
    __tablename__ = "genres"

    name = Column("genre", VARCHAR(255), nullable=False, unique=True)

