from datetime import datetime
import os

from miner import yahoo, wsj
from archive import dump

symbols = ("C6L", "J7X", "S53", "C52", "N03", "Z74", "CC3", "B2F")
start_date = datetime(2004, 3, 1)
end_date = datetime(2014, 3, 1)

archive_directory = "/home/kakarukeys/ownCloud/Fundamental Analysis project/archive"
yahoo_archive_directory = os.path.join(archive_directory, "yahoo")
wsj_archive_directory = os.path.join(archive_directory, "wsj")

data = yahoo.get_historical_data(symbols, start_date, end_date)
dump(data, yahoo_archive_directory, "historicaldata", "csv")

for table_name in yahoo.FINANCIAL_TABLE_NAMES:
    data = yahoo.get_financial_data(symbols, table_name, "annual")
    dump(data, yahoo_archive_directory, table_name, "json")

for report_type in wsj.FINANCIAL_REPORT_TYPES:
    data = {s: wsj.get_financial_data(s, "annual", report_type) for s in symbols}
    dump(data, wsj_archive_directory, report_type, "json")
