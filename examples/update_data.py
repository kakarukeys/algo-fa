import csv
import logging

from fa.miner import yahoo
from fa.piping import csv_string_to_records
from fa.util import partition
from fa.database.query import get_symbols_to_update_data, update_historical_prices

import initialize
from settings import *


""" Download data from internet to database """

initialize.init()
logger = logging.getLogger(__name__)

logger.info("Will perform data update on all symbols not up to date on {0}.".format(end_date))
all_symbols = get_symbols_to_update_data(end_date)

# do the download in chunks of size 8 to prevent overloading servers
for symbols in partition(all_symbols, 8):
    data = yahoo.get_historical_data(symbols, start_date, end_date)

    for symbol, csv_string in data.items():
        if csv_string:
            try:
                records = csv_string_to_records(symbol, csv_string, strict=True)
                update_historical_prices(symbol, records, end_date)
            except csv.Error as e:
                logger.exception(e)
                logger.error("csv of {0} is malformed.".format(symbol))
        else:
            logger.warning("Could not find updated historical prices of {0}.".format(symbol))
