import os
import numpy as np
import pandas as pd
from pandas.io.parsers import read_csv


HISTORICAL_DATA_COLUMNS = {
	"Open": np.float64,
	"High": np.float64,
	"Low": np.float64,
	"Close": np.float64,
	"Volume": np.int64,
	"Adj Close": np.float64,
}

def load_historical_data_single_symbol(archive_directory, symbol, columns=None):
	""" Returns a DataFrame object containing historical data of symbol with columns, loaded from archive.
		archive_directory: archive directory path
		symbol: stock symbol
		columns: a collection of column names as defined in HISTORICAL_DATA_COLUMNS, None - include all.
	"""
	filepath = os.path.join(archive_directory, "yahoo/historicaldata", symbol + ".csv")

	if columns is not None:
		columns = ["Date"] + list(columns)

	with open(filepath) as f:
		return read_csv(f, dtype=HISTORICAL_DATA_COLUMNS, index_col=0, parse_dates=True, usecols=columns)

def load_historical_data(archive_directory, symbols, columns=None):
	""" Returns a Panel object containing historical data of symbols with columns, loaded from archive.
		archive_directory: archive directory path
		symbol: a collection of stock symbols
		columns: a collection of column names as defined in HISTORICAL_DATA_COLUMNS, None - include all.
	"""
	return pd.Panel({s: load_historical_data_single_symbol(archive_directory, s, columns) for s in symbols})
