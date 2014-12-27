import csv
import logging

from fa.miner import yahoo
from fa.piping import csv_string_to_records
from fa.util import partition
from fa.database.query import get_outdated_symbols, update_fundamentals

import initialize
from settings import *


""" Download data from internet to database """

initialize.init()
logger = logging.getLogger(__name__)

logger.info("Will update historical prices of all symbols not up to date on {0}.".format(end_date))
all_symbols = [s.symbol for s in get_outdated_symbols("price", end_date)]

# do the download in chunks of size 8 to prevent overloading servers
for symbols in partition(all_symbols, 8):
    data = yahoo.get_historical_data(symbols, start_date, end_date)

    for symbol, csv_string in data.items():
        if csv_string:
            try:
                records = csv_string_to_records(symbol, csv_string, strict=True)
                update_fundamentals("price", symbol, records, end_date, delete_old=True)
            except csv.Error as e:
                logger.exception(e)
                logger.error("csv of {0} is malformed.".format(symbol))
        else:
            logger.warning("Could not find updated historical prices of {0}. Skip.".format(symbol))
