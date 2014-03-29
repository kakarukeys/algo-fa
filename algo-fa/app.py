from datetime import datetime

from miner import get_historical_data, get_financial_data, FINANCIAL_TABLE_NAMES
from archive import dump


symbols = ("C6L", "J7X", "S53", "C52", "N03", "Z74", "CC3", "B2F")
start_date = datetime(2004, 3, 1)
end_date = datetime(2014, 3, 1)
archive_directory = "/home/kakarukeys/ownCloud/Fundamental Analysis project/archive"

data = get_historical_data(symbols, start_date, end_date)
dump(data, archive_directory, "historicaldata", "csv")

for table_name in FINANCIAL_TABLE_NAMES:
    data = get_financial_data(symbols, table_name)
    dump(data, archive_directory, table_name, "json")
