import logging

from fa.database.models import db

from settings import db_path, log_file_path, log_level


""" Initialization """

def init():
    # connect to database
    db.init(db_path)
    db.connect()

    # set up logging
    logging.basicConfig(filename=log_file_path, level=log_level)
