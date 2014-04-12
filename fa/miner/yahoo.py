import requests


SGX_SUFFIX = "SI"
HISTORICAL_DATA_API_URL_TEMPLATE = "http://ichart.yahoo.com/table.csv?s={symbol}&a={startmonth}&b={startday}&c={startyear}&d={endmonth}&e={endday}&f={endyear}&g=m&ignore=.csv"
YQL_TEMPLATE_1 = "SELECT * FROM {table} WHERE symbol IN {symbols}"
YQL_TEMPLATE_2 = " AND timeframe='{timeframe}'"
YQL_API_URL = "http://query.yahooapis.com/v1/public/yql"
FINANCIAL_REPORT_TYPES = ("balancesheet", "cashflow", "incomestatement", "keystats")

def get_full_symbol(s):
	return s + '.' + SGX_SUFFIX

def get_abcdef(start_date, end_date):
	return {
		'startmonth': start_date.month - 1,
		'startday': start_date.day,
		'startyear': start_date.year,
		'endmonth': end_date.month - 1,
		'endday': end_date.day,
		'endyear': end_date.year,
	}

def get_historical_data(symbols, start_date, end_date):
	"""	Returns {"symbol": "historical data in csv string"}:

		>>> get_historical_data(("C6L", "ZZZZZZ",), datetime(2004, 3, 1), datetime(2014, 3, 1))
		{"C6L": "...", "ZZZZZZ": ''}
	"""
	abcdef = get_abcdef(start_date, end_date)

	result = {}
	for s in symbols:
		url = HISTORICAL_DATA_API_URL_TEMPLATE.format(symbol=get_full_symbol(s), **abcdef)
		r = requests.get(url)
		result[s] = r.text if r.status_code == 200 else ''

	return result

def construct_yql(symbols, table, timeframe):
	full_symbols = '({0})'.format(','.join(repr(get_full_symbol(s)) for s in symbols))
	yql = YQL_TEMPLATE_1.format(table=table, symbols=full_symbols)

	if timeframe:
		yql += YQL_TEMPLATE_2.format(timeframe=timeframe)

	return yql

def get_financial_data(symbols, timeframe, report_type):
	"""	Returns {"symbol": financial data in a dictionary}:
		symbols: e.g. ("C6L", "B9K",)
		timeframe: "annual" or "quarterly"
		report_type: any string in FINANCIAL_REPORT_TYPES
	"""
	yql = construct_yql(
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
