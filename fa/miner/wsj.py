import requests
from bs4 import BeautifulSoup


WSJ_URL_TEMPLATE = "http://quotes.wsj.com/SG/{symbol}/financials/{timeframe}/{report_type}"
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

def get_financial_data(symbol, timeframe, report_type):
    """ Returns financial data in a dictionary.
        symbol: e.g. "C6L"
        timeframe: "annual" or "quarter"
        report_type: any string in FINANCIAL_REPORT_TYPES
    """
    html = get_report_html(symbol, timeframe, report_type)
    soup = BeautifulSoup(html)
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
