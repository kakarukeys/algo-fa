import re
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from functools import partial
from collections import defaultdict

import numpy as np


TOP_REMARK_RE = re.compile(
    r"Fiscal.+ [A-Za-z]+-(?P<fiscal_year_end_month>[A-Za-z]+)\..+values (?P<currency>[A-Z]+) (?P<value_unit>[A-Za-z]+)\.",
    re.IGNORECASE
)

VALUE_UNITS = {
    "thousands": 1000,
    "millions": 1000000,
    "billions": 1000000000,
}

# these columns have value_unit 1
# percentage columns need not be listed here, because they are auto-recognized to have value_unit 1
UNO_VALUE_UNIT_COLUMNS = {
    "EPS (Basic)",
    "EPS (Diluted)",
    "Asset Turnover",
    "Current Ratio",
    "Quick Ratio",
    "Cash Ratio"
}

def _parse_top_remark(string):
    """ top remark string -> month (integer) where fiscal year ends, currency (string), value unit (multiple of 1,000) """
    result = TOP_REMARK_RE.match(string)

    if result:
        end_month = result.group("fiscal_year_end_month")
        currency = result.group("currency")
        value_unit = result.group("value_unit")

        return datetime.strptime(end_month, "%B").month, currency.upper(), VALUE_UNITS[value_unit.lower()]
    else:
        raise ValueError("Top remark cannot be parsed.")

def _calc_financial_data_date(fiscal_year_end_month, period):
    """ Returns a numpy datetime64 object which is the date after the fiscal year of <period> just ended.
        fiscal_year_end_month: 1~12
        period: e.g. 2013
    """
    d = date(period, fiscal_year_end_month, 1) + relativedelta(months=1)
    return np.datetime64(d)

def _deduplicate_column_name(data):
    """ Yields (deduplicated column name, values) by iterating over <data>,
        appending _incremental number to each duplicate column name.
        data: a sequence of (column_name, values)
    """
    counter = defaultdict(int)
    for column_name, values in data:
        counter[column_name] += 1

        suffix = '' if counter[column_name] == 1 else '_{0}'.format(counter[column_name])
        yield column_name + suffix, values

def _parse_value(string, value_unit):
    """ value string -> numpy-typed value
        value_unit: a number which the resultant value except percentage will be multiplifed by
    """
    if string == '-':
        return np.nan
    else:
        s = string.replace(',', '')
        if s.endswith('%'):
            return np.float64(s.rstrip('%')) / 100
        else:
            s = s.replace('(', '-').rstrip(')')
            if '.' in s:
                return np.float64(s) * value_unit
            else:
                return np.int64(s) * value_unit

def preprocess(obj):
    """ Preprocesses <obj>, parses the values, yields column name, list of parsed values

        obj: dictionary of scraped raw data.
    """
    assert obj["timeframe"] == "annual"

    fiscal_year_end_month, currency, value_unit = _parse_top_remark(obj["top_remark"])
    assert currency == "SGD"
    calc_date = partial(_calc_financial_data_date, fiscal_year_end_month)

    first_row = obj["data"][0]
    assert first_row[0] == "periods"
    yield "Date", [calc_date(int(d)) for d in first_row[1]]

    for column_name, values in _deduplicate_column_name(obj["data"][1:]):
        value_unit_to_use = 1 if column_name in UNO_VALUE_UNIT_COLUMNS else value_unit
        yield column_name, [_parse_value(v, value_unit_to_use) for v in values]
