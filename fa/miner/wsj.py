import re

import requests
from bs4 import BeautifulSoup

from fa.miner.preprocess import preprocess
from fa.util import transpose_items


WSJ_URL_TEMPLATE = "http://quotes.wsj.com/SG/{symbol}/financials/{timeframe}/{report_type}"
WSJ_URL_RE = re.compile(r"http://quotes.wsj.com/SG/(?P<symbol>\w+)/financials/(?P<timeframe>[a-z]+)/(?P<report_type>[a-z\-]+)")
FINANCIAL_REPORT_TYPES = ("balance-sheet", "cash-flow", "income-statement")

def get_report_html(symbol, timeframe, report_type):
    """ Returns report page HTML.
        symbol: e.g. "C6L"
        timeframe: "annual" or "quarter"
        report_type: any string in FINANCIAL_REPORT_TYPES
    """
    url = WSJ_URL_TEMPLATE.format(symbol=symbol, timeframe=timeframe, report_type=report_type)
    r = requests.get(url)
    return r.text

def _scrape_row(tr):
    return tr.select("td.rowTitle")[0].text.strip(), [e.text.strip() for e in tr.select("td.valueCell")]

def _scrape_html(html):
    """ Performs soup work on <html> string to extract the relevant information and returns it in a dictionary. """
    soup = BeautifulSoup(html)

    link = soup.select("link[rel=canonical]")[0]["href"]
    symbol, timeframe, report_type = WSJ_URL_RE.match(link).groups()

    tables = soup.select("table.crDataTable")
    table_header = tables[0].select("tr.topRow > th")

    result = {
        "symbol": symbol,
        "timeframe": timeframe,
        "report_type": report_type,
        "top_remark": table_header[0].text,
        "data": [
            ("periods", [e.text.strip() for e in table_header[1:-1]]),
        ]
    }

    result["data"] += [_scrape_row(tr) for tbl in tables for tr in tbl.tbody.select("tr")]

    return result

def get_financial_data(symbol, timeframe, report_type):
    """ Returns financial data in an iterator of csv rows (tuples). First row will be the headers.
        symbol: e.g. "C6L"
        timeframe: "annual" or "quarter"
        report_type: any string in FINANCIAL_REPORT_TYPES
    """
    html = get_report_html(symbol, timeframe, report_type)
    raw_data = _scrape_html(html)
    items = preprocess(raw_data)
    return transpose_items(items)
