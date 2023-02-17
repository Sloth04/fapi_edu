# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import VARCHAR, BOOLEAN, ENUM

from helpers.mixins import MysqlPrimaryKeyMixin, MysqlTimestampsMixin
from src.database import Base
from src.schemas import Role


class User(Base, MysqlPrimaryKeyMixin, MysqlTimestampsMixin):
    __tablename__ = "users"

    username = Column("username", VARCHAR(255), nullable=False, index=True)
    email = Column("email", VARCHAR(255), nullable=False, index=True)
    hashed_password = Column("hashed_password", VARCHAR(255), nullable=False)
    full_name = Column("full_name", VARCHAR(255), nullable=True)
    otp_secret = Column("otp_secret", VARCHAR(255), nullable=False)
    disable = Column("disable", BOOLEAN(), nullable=False, default=False)
    role = Column("role", ENUM(Role))
