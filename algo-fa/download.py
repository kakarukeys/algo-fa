from miner import yahoo, wsj
from archive import dump
from settings import *


"""Download all the data from internet to archive"""

if __name__ == "__main__":
	data = yahoo.get_historical_data(symbols, start_date, end_date)
	dump(data, yahoo_archive_directory, "historicaldata", "csv")

	for table_name in yahoo.FINANCIAL_TABLE_NAMES:
	    data = yahoo.get_financial_data(symbols, table_name, "annual")
	    dump(data, yahoo_archive_directory, table_name, "json")

	for report_type in wsj.FINANCIAL_REPORT_TYPES:
	    data = {s: wsj.get_financial_data(s, "annual", report_type) for s in symbols}
	    dump(data, wsj_archive_directory, report_type, "json")
