from fa.database.models import db, export
from settings import db_path


""" Initialization script """

# create tables
db.init(db_path)
db.create_tables(export)
