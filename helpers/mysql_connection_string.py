# -*- coding: utf-8 -*-
import settings


def mysql_connection_string() -> str:
    """Returns mysql connection string"""
    return "mysql+mysqldb://{}:{}@{}:{}/{}?charset=utf8mb4".format(
        settings.DB_USERNAME,
        settings.DB_PASSWORD,
        settings.DB_HOST,
        settings.DB_PORT,
        settings.DB_DATABASE,
    )