import requests


HISTORICAL_DATA_API_URL_TEMPLATE = "http://ichart.yahoo.com/table.csv?s={symbol}&a={startmonth}&b={startday}&c={startyear}&d={endmonth}&e={endday}&f={endyear}&g=m&ignore=.csv"
SGX_SUFFIX = "SI"

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
	"""	Returns {"symbol": "historical data in csv string"}:

		>>> get_historical_data(("C6L", "ZZZZZZ",), datetime(2004, 3, 1), datetime(2014, 3, 1))
		{"C6L": "...", "ZZZZZZ": ''}
	"""
	abcdef = _get_abcdef(start_date, end_date)

	result = {}
	for s in symbols:
		url = HISTORICAL_DATA_API_URL_TEMPLATE.format(symbol=s + '.' + SGX_SUFFIX, **abcdef)
		r = requests.get(url)
		result[s] = r.text if r.status_code == 200 else ''

	return result
