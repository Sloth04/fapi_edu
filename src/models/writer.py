# -*- coding: utf-8 -*-
import datetime

import sqlalchemy
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import VARCHAR, DATE

from helpers.mixins import MysqlPrimaryKeyMixin, MysqlTimestampsMixin
from src.database import Base


class Writer(Base, MysqlPrimaryKeyMixin, MysqlTimestampsMixin):
    __tablename__ = "writers"

    name = Column("name", VARCHAR(255), nullable=False)
    lastname = Column("lastname", VARCHAR(255), nullable=False)
    born = Column("born", DATE(), nullable=False, default=datetime.date.today(),
                  server_default=sqlalchemy.text('(CURRENT_DATE())'))
    died = Column("died", DATE(), nullable=True)
