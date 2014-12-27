import logging

from fa.database.models import db

from settings import db_path, log_file_path, log_level


""" Initialization """

def init():
    # connect to database
    db.init(db_path)
    db.connect()

    # http://stackoverflow.com/questions/9937713/does-sqlite3-not-support-foreign-key-constraints
    # In SQLite 3.x, you have to make the following query every time you connect to an SQLite database
    # Otherwise SQLite will ignore all foreign key constraints.
    db.execute_sql("PRAGMA foreign_keys = ON")

    # set up logging
    logging.basicConfig(
        filename=log_file_path,
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
