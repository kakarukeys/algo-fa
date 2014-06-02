from fa.miner import yahoo, wsj
from fa.archive.save import dump

from settings import *


""" Download all the data from internet to archive """

if __name__ == "__main__":
    data = yahoo.get_historical_data(symbols, start_date, end_date)
    dump(data, yahoo_archive_directory, "historicaldata")

    for report_type in yahoo.FINANCIAL_REPORT_TYPES:
        data = yahoo.get_financial_data(symbols, "annual", report_type)
        dump(data, yahoo_archive_directory, report_type)

    for report_type in wsj.FINANCIAL_REPORT_TYPES:
        data = {s: wsj.get_financial_data(s, "annual", report_type) for s in symbols}
        dump(data, wsj_archive_directory, report_type)
