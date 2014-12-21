from fa.database.models import db, export
import initialize


""" Create all tables for algorithmic fundamental analysis """

initialize.init()
db.create_tables(export)
