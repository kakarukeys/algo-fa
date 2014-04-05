import json, os, re
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from functools import partial

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

TOP_REMARK_RE = re.compile(
	r"Fiscal.+ [A-Za-z]+-(?P<fiscal_year_end_month>[A-Za-z]+)\..+values (?P<currency>[A-Z]+) (?P<value_unit>[A-Za-z]+)\.",
	re.IGNORECASE
)

VALUE_UNITS = {
	"thousands": 1000,
	"millions": 1000000,
	"billions": 1000000000,
}

def load_historical_data_single_symbol(archive_directory, symbol, columns=None):
	""" Returns a DataFrame object containing historical data of <symbol> with <columns>, loaded from <archive_directory>.
		columns: a collection of column names as defined in HISTORICAL_DATA_COLUMNS, None - include all.
	"""
	filepath = os.path.join(archive_directory, "yahoo/historicaldata", symbol + ".csv")

	if columns is not None:
		columns = ["Date"] + list(columns)

	with open(filepath) as f:
		return read_csv(f, dtype=HISTORICAL_DATA_COLUMNS, index_col=0, parse_dates=True, usecols=columns)

def load_historical_data(archive_directory, symbols, columns=None):
	""" Returns a Panel object containing historical data of <symbols> with <columns>, loaded from <archive_directory>.
		symbols: a collection of stock symbols
		columns: a collection of column names as defined in HISTORICAL_DATA_COLUMNS, None - include all.
	"""
	return pd.Panel({s: load_historical_data_single_symbol(archive_directory, s, columns) for s in symbols})

def parse_top_remark(string):
	""" top remark string -> month (integer) where fiscal year ends, currency, value unit (multiple of 1,000) """
	result = TOP_REMARK_RE.match(string)

	end_month = result.group("fiscal_year_end_month")
	currency = result.group("currency")
	value_unit = result.group("value_unit")

	return datetime.strptime(end_month, "%B").month, currency.upper(), VALUE_UNITS[value_unit.lower()]

def calc_financial_data_date(fiscal_year_end_month, period):
	""" Returns a numpy datetime64 object which is the date after the fiscal year of <period> just ended.
		fiscal_year_end_month: 1~12
		period: e.g. 2013
	"""
	d = date(period, fiscal_year_end_month, 1) + relativedelta(months=1)
	return np.datetime64(d)

def parse_value(string):
	""" value string -> numpy-typed value """
	if string == '-':
		return np.nan
	elif string.endswith('%'):
		return np.float64(string.rstrip('%')) / 100
	else:
		s = string.replace(',', '').replace('(', '-').rstrip(')')
		if '.' in string:
			return np.float64(s)
		else:
			return np.int64(s)

def preprocess(obj, extract_columns):
	""" Preprocesses <obj>, parses the values, extracts columns in <extract_columns>
		yields column name, list of parsed values

		obj: object parsed from json.
		extract_columns: set of column name strings, None - extract all.
	"""
	assert obj["timeframe"] == "annual"

	fiscal_year_end_month, currency, value_unit = parse_top_remark(obj["top_remark"])
	assert currency == "SGD"
	calc_date = partial(calc_financial_data_date, fiscal_year_end_month)

	first_row = obj["data"][0]
	assert first_row[0] == "periods"
	yield "Date", [calc_date(int(d)) for d in first_row[1]]

	for column_name, values in obj["data"][1:]:
		if extract_columns is None or column_name in extract_columns:
			yield column_name, [parse_value(v) for v in values]

def load_financial_data_single_symbol(archive_directory, report_type, symbol, columns=None):
	""" Returns a DataFrame object containing <report_type> financial data of <symbol> with <columns>, loaded from <archive_directory>.
		report_type: report type as defined in miner.wsj.FINANCIAL_REPORT_TYPES
		columns: a collection of column names as defined in the json file, None - include all.
	"""
	filepath = os.path.join(archive_directory, "wsj", report_type, symbol + ".json")

	with open(filepath) as f:
		j = json.load(f)

	extract_columns = None if columns is None else set(columns)

	df = pd.DataFrame.from_items(preprocess(j, extract_columns))
	df.set_index("Date", inplace=True)

	return df
