import json, os

import numpy as np
import pandas as pd
from pandas.io.parsers import read_csv

from fa.miner.wsj import FINANCIAL_REPORT_TYPES
from fa.archive.preprocess import preprocess


HISTORICAL_DATA_COLUMNS = {
    "Open": np.float64,
    "High": np.float64,
    "Low": np.float64,
    "Close": np.float64,
    "Volume": np.int64,
    "Adj Close": np.float64,
}

def load_historical_data(archive_directory, symbol, columns=None):
    """ Returns a DataFrame object containing historical data of <symbol> with <columns>, loaded from <archive_directory>.
        columns: a collection of column names as defined in HISTORICAL_DATA_COLUMNS, None - include all.
    """
    filepath = os.path.join(archive_directory, "yahoo/historicaldata", symbol + ".csv")

    if columns is not None:
        columns = ["Date"] + list(columns)

    with open(filepath) as f:
        df = read_csv(f, dtype=HISTORICAL_DATA_COLUMNS, index_col=0, parse_dates=True, usecols=columns)
    df.sort_index(inplace=True)

    return df

def load_historical_data_multiple(archive_directory, symbols, columns=None):
    """ Returns a Panel object containing historical data of <symbols> with <columns>, loaded from <archive_directory>.
        symbols: a collection of stock symbols
        columns: a collection of column names as defined in HISTORICAL_DATA_COLUMNS, None - include all.
    """
    return pd.Panel({s: load_historical_data(archive_directory, s, columns) for s in symbols})


def load_financial_data(archive_directory, report_type, symbol, columns=None):
    """ Returns a DataFrame object containing <report_type> financial data of <symbol> with <columns>, loaded from <archive_directory>.
        report_type: report type as defined in FINANCIAL_REPORT_TYPES
        columns: a collection of column names as defined in the actual json file in archive, None - include all.
    """
    filepath = os.path.join(archive_directory, "wsj", report_type, symbol + ".json")

    with open(filepath) as f:
        j = json.load(f)

    extract_columns = None if columns is None else set(columns)

    df = pd.DataFrame.from_items(list(preprocess(j, extract_columns)))
    df.set_index("Date", inplace=True)
    df.sort_index(inplace=True)

    return df

def load_financial_data_all(archive_directory, symbol, columns=None):
    """ Returns {report_type: financial report DataFrame object} of <symbol> with <columns>, loaded from <archive_directory>.
        columns: a collection of column names as defined in the actual json file in archive, None - include all.
    """
    return {rt: load_financial_data(archive_directory, rt, symbol, columns) for rt in FINANCIAL_REPORT_TYPES}
