import logging

from fa.miner import wsj
from fa.miner.exceptions import MinerException
from fa.database.query import get_outdated_symbols, get_record_dates, update_fundamentals
from fa.piping import csv_rows_to_records

import initialize
from settings import *


""" Download data from internet to database """

initialize.init()
logger = logging.getLogger(__name__)

for report_type in wsj.FINANCIAL_REPORT_TYPES:
    logger.info("Will update {0} data of all symbols not up to date on {1}.".format(report_type, end_date))

    data_type = report_type.replace('-', '_')
    symbol_update_dates = {s.symbol: s.updated_at for s in get_outdated_symbols(data_type, end_date)}

    for symbol in symbol_update_dates:
        try:
            data = wsj.get_financial_data(symbol, "annual", report_type)
        except MinerException as e:
            logger.warning("Could not find updated {0} data of {1}. Skip.".format(report_type, symbol))
            continue
        else:
            records = list(csv_rows_to_records(symbol, data))

            if symbol_update_dates[symbol]:
                logger.info("Filter out {0} records of {1} that already exist".format(report_type, symbol))
                existing_record_dates = set(r.date for r in get_record_dates(data_type, symbol))
                records = [r for r in records if r["date"] not in existing_record_dates]

            if records:
                update_fundamentals(data_type, symbol, records, end_date)
            else:
                logger.info("No new {0} data for {1}.".format(report_type, symbol))

    logger.info("Finished updating {0} data.".format(report_type))
