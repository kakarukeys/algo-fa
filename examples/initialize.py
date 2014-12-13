from fa.models import db, Stock, MarketIndex
from settings2 import db_path


# create tables

db.init(db_path)
db.create_tables([Stock, MarketIndex])
