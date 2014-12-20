import logging
import requests


logger = logging.getLogger(__name__)

SGX_SUFFIX = "SI"
HISTORICAL_DATA_API_URL_TEMPLATE = "http://ichart.yahoo.com/table.csv?s={symbol}&a={startmonth}&b={startday}&c={startyear}&d={endmonth}&e={endday}&f={endyear}&g=d&ignore=.csv"
YQL_TEMPLATE_1 = "SELECT * FROM {table} WHERE symbol IN {symbols}"
YQL_TEMPLATE_2 = " AND timeframe='{timeframe}'"
YQL_API_URL = "http://query.yahooapis.com/v1/public/yql"
FINANCIAL_REPORT_TYPES = ("balancesheet", "cashflow", "incomestatement", "keystats")

def _get_abcdef(start_date, end_date):
    return {
        'startmonth': start_date.month - 1,
        'startday': start_date.day,
        'startyear': start_date.year,
        'endmonth': end_date.month - 1,
        'endday': end_date.day,
        'endyear': end_date.year,
    }

def get_historical_data(symbols, start_date, end_date):
    """ Returns {"symbol": "historical data in csv string"}:
        (blank string if there is an error.)

        >>> get_historical_data(("C6L", "ZZZZZZ",), datetime(2004, 3, 1), datetime(2014, 3, 1))
        {"C6L": "...", "ZZZZZZ": ''}
    """
    logger.info("getting historical data of %s from %s to %s", ','.join(symbols), start_date, end_date)
    abcdef = _get_abcdef(start_date, end_date)

    result = {}
    for s in symbols:
        url = HISTORICAL_DATA_API_URL_TEMPLATE.format(symbol=s, **abcdef)
        try:
            r = requests.get(url)
        except requests.exceptions.RequestException as e:
            logger.exception(e)
            result[s] = ''
        else:
            if r.status_code == 200:
                result[s] = r.text
            else:
                logger.warning("GET %s %s %s", r.url, r.status_code, r.reason)
                result[s] = ''

    return result

def _construct_yql(symbols, table, timeframe):
    full_symbols = '({0})'.format(','.join(map(repr, symbols)))
    yql = YQL_TEMPLATE_1.format(table=table, symbols=full_symbols)

    if timeframe:
        yql += YQL_TEMPLATE_2.format(timeframe=timeframe)

    return yql

def get_financial_data(symbols, timeframe, report_type):
    """ Returns {"symbol": financial data in a dictionary}:
        symbols: e.g. ("C6L", "B9K",)
        timeframe: "annual" or "quarterly"
        report_type: any string in FINANCIAL_REPORT_TYPES
    """
    yql = _construct_yql(
        symbols,
        "yahoo.finance." + report_type,
        None if report_type == "keystats" else timeframe
    )
    params = {
        "q": yql,
        "format": "json",
        "env": "store://datatables.org/alltableswithkeys",
    }
    r = requests.get(YQL_API_URL, params=params)

    results = r.json()["query"]["results"]["stats" if report_type == "keystats" else report_type]

    if isinstance(results, dict):
        results = [results]

    return {rs["symbol"].split('.')[0]: rs for rs in results}
