import csv
import logging

from fa.database.models import db, Symbol, Price, export


logger = logging.getLogger(__name__)

def get_symbols_to_update_data(end_date):
    """ Gets symbols which data is never updated or was updated before <end_date>
        end_date: datetime object
    """
    return [s.symbol for s in Symbol.select(Symbol.symbol).where(
        (Symbol.price_updated_at < end_date) | (Symbol.price_updated_at == None)
    )]

def update_historical_prices(symbol, records, end_date):
    """ Updates historical prices of <symbol> with <records> and mark it as updated at <end_date>.
        records: a sequence of maps
        end_date: datetime object
    """
    logger.info("Updating historical prices of {0} in database...".format(symbol))
    try:
        with db.transaction():
            Price.delete().where(Price.symbol_obj == symbol).execute()  # there may be adjustment to existing prices
            for rec in records:
                Price.create(**rec)
            Symbol.update(price_updated_at=end_date).where(Symbol.symbol == symbol).execute()
    except Exception as e:
        logger.exception(e)
        logger.debug("Was trying to insert a record: {0}".format(rec))
        logger.error("Historical prices of {0} are not updated.".format(symbol))
        raise

def delete_all():
    for Model in export:
        Model.delete().execute()
