import logging
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
from functools import partial
from collections import defaultdict

from fa.miner.symbol_suffix import SYMBOL_SUFFIX_INFO, DEFAULT_CURRENCY
from fa.miner.exceptions import PreprocessingError
from fa.util import assert_equal


logger = logging.getLogger(__name__)

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
        raise PreprocessingError("Top remark cannot be parsed.")

def _validate(obj, actual_currency, symbol, timeframe, report_type):
    """ Verifies whether <obj> is good for value parsing.
        obj: dictionary of scraped raw data
        actual_currency: currency used, derived from <obj>
        symbol, timeframe, report_type: the parameters that were used to obtain <obj>
    """
    prefix, _, suffix = symbol.partition('.')

    # symbol, timeframe, report_type
    assert_equal(obj["symbol_prefix"], prefix, "symbol prefix")
    assert_equal(obj["timeframe"], timeframe, "timeframe")
    assert_equal(obj["report_type"], report_type, "report_type")

    # currency
    expected_currency = SYMBOL_SUFFIX_INFO[suffix][2] if suffix else DEFAULT_CURRENCY
    assert_equal(actual_currency, expected_currency, "currency")

    # first column's name
    data = obj["data"]
    assert_equal(data[0][0], "periods", "first column's name")

    # column length
    column_lengths = set(len(p[1]) for p in data)
    assert len(column_lengths) == 1, "All columns are expected to have the same length, but they do not"

def _calc_financial_data_date(fiscal_year_end_month, period):
    """ Returns a datetime object which is the date after the fiscal year of <period> just ended.
        fiscal_year_end_month: 1~12
        period: e.g. 2013
    """
    return datetime(period, fiscal_year_end_month, 1) + relativedelta(months=1)

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
    """ string -> value of a type
        value_unit: a number which the resultant value except percentage will be multiplifed by
    """
    if string == '-':
        return None
    else:
        s = string.replace(',', '')
        if s.endswith('%'):
            return float(s.rstrip('%')) / 100
        else:
            s = s.replace('(', '-').rstrip(')')
            if '.' in s:
                return float(s) * value_unit
            else:
                return int(s) * value_unit

def preprocess(obj, symbol, timeframe, report_type):
    """ Preprocesses <obj>, parses the values, yields column name, list of parsed values

        obj: dictionary of scraped raw data.
        symbol, timeframe, report_type: the parameters that were used to obtain <obj>.
    """
    logger.info("preprocessing raw data of {0} {1} {2}".format(symbol, timeframe, report_type))

    fiscal_year_end_month, currency, value_unit = _parse_top_remark(obj["top_remark"])
    _validate(obj, currency, symbol=symbol, timeframe=timeframe, report_type=report_type)

    calc_date = partial(_calc_financial_data_date, fiscal_year_end_month)
    yield "Date", [calc_date(int(d)) for d in obj["data"][0][1]]

    for column_name, values in _deduplicate_column_name(obj["data"][1:]):
        value_unit_to_use = 1 if column_name in UNO_VALUE_UNIT_COLUMNS else value_unit
        yield column_name, [_parse_value(v, value_unit_to_use) for v in values]
