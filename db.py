from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine.url import make_url
from sqlalchemy_utils import (
    database_exists as database_exists_util,
    create_database as create_database_util,
)


def create_database():
    url = make_url(current_app.config["SQLALCHEMY_DATABASE_URI"])
    if url.drivername == "postgres":
        url.drivername = "postgresql"

    if url.drivername.startswith("mysql"):
        url.query["charset"] = "utf8mb4"

    # Creates database if the database database does not exist
    if not database_exists_util(url):
        if url.drivername.startswith("mysql"):
            create_database_util(url, encoding="utf8mb4")
        else:
            create_database_util(url)
    return url


db = SQLAlchemy()
