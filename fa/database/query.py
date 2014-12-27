import logging
from fa.database.models import *


logger = logging.getLogger(__name__)

def get_outdated_symbols(data_type, end_date):
    """ Gets symbols which <data_type> data is never updated or was updated before <end_date>, and their update dates.

        data_type: name of *_updated_at fields in Symbol model without _updated_at
        end_date: datetime object
    """
    field = getattr(Symbol, data_type + "_updated_at")
    return Symbol.select(Symbol.symbol, field.alias("updated_at")).where((field < end_date) | (field == None))

def get_record_dates(data_type, symbol):
    """ data_type: name of *_updated_at fields in Symbol model without _updated_at
        symbol: e.g. 'C6L.SI'
    """
    Model = get_Model(data_type)
    return Model.select(Model.date).where(Model.symbol_obj == symbol)

def update_fundamentals(data_type, symbol, records, end_date, delete_old=False):
    """ Updates fundamentals of <symbol> with <records> and mark it as updated at <end_date>.

        data_type: name of *_updated_at fields in Symbol model without _updated_at
        symbol: e.g. 'C6L.SI'
        records: a sequence of maps
        end_date: datetime object
        delete_old: whether to delete all old records of <symbol> first
    """
    logger.info("Updating {0} data of {1} in database...".format(data_type, symbol))

    Model = get_Model(data_type)
    marker_map = {data_type + "_updated_at": end_date}

    try:
        with db.transaction():
            if delete_old:  # do this when there may be e.g. price adjustment
                Model.delete().where(Model.symbol_obj == symbol).execute()

            for rec in records:
                Model.create(**rec)

            Symbol.update(**marker_map).where(Symbol.symbol == symbol).execute()

    except Exception as e:
        logger.exception(e)
        logger.debug("Was trying to insert a record: {0}".format(rec))
        logger.error("{0} data of {1} is not updated.".format(data_type, symbol))
        raise

def delete_all():
    for Model in reversed(export):  # delete data from dependent models first
        Model.delete().execute()
