from datetime import datetime
import requests


HISTORICAL_DATA_API_URL_TEMPLATE = "http://ichart.yahoo.com/table.csv?s={symbol}&a={startmonth}&b={startday}&c={startyear}&d={endmonth}&e={endday}&f={endyear}&g=m&ignore=.csv"
SGX_SUFFIX = "SI"

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
	abcdef = get_abcdef(start_date, end_date)

	for s in symbols:
		url = HISTORICAL_DATA_API_URL_TEMPLATE.format(symbol=s + '.' + SGX_SUFFIX, **abcdef)
		r = requests.get(url)
		print(s)
		print(r.text)

symbols = ("C6L", "J7X",)# "S53", "C52", "N03", "Z74", "CC3", "B2F")
start_date = datetime(2004, 3, 1)
end_date = datetime(2014, 3, 1)
get_historical_data(symbols, start_date, end_date)
