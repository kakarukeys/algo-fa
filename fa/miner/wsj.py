import logging
import re

from bs4 import BeautifulSoup

from fa.miner.symbol_suffix import SYMBOL_SUFFIX_INFO
from fa.miner.http import strict_get
from fa.miner.preprocess import preprocess
from fa.miner.exceptions import SymbolError, ScrapingError, PreprocessingError
from fa.util import transpose_items


logger = logging.getLogger(__name__)

WSJ_URL_TEMPLATE = "http://quotes.wsj.com/{country_mic}{symbol}/financials/{timeframe}/{report_type}"
WSJ_URL_RE = re.compile(r"http://quotes.wsj.com/SG/(?P<symbol>\w+)/financials/(?P<timeframe>[a-z]+)/(?P<report_type>[a-z\-]+)")
FINANCIAL_REPORT_TYPES = ("balance-sheet", "cash-flow", "income-statement")

def _get_report_url(symbol, timeframe, report_type):
    """ Returns report page URL. """
    prefix, _, suffix = symbol.partition('.')

    if suffix:
        if suffix in SYMBOL_SUFFIX_INFO:
            country_mic = '{0}/{1}/'.format(*SYMBOL_SUFFIX_INFO[suffix][:2])
        else:
            msg = "The suffix {0} of {1} is not listed in SYMBOL_SUFFIX_INFO.".format(suffix, symbol)
            logger.error(msg)
            raise SymbolError(msg)
    else:
        country_mic = ''

    return WSJ_URL_TEMPLATE.format(country_mic=country_mic, symbol=prefix, timeframe=timeframe, report_type=report_type)

def _scrape_row(tr):
    return tr.select("td.rowTitle")[0].text.strip(), [e.text.strip() for e in tr.select("td.valueCell")]

def _scrape_html(html):
    """ Performs soup work on <html> string to extract the relevant information and returns it in a dictionary. """
    soup = BeautifulSoup(html)

    link = soup.select("link[rel=canonical]")[0]["href"]
    symbol, timeframe, report_type = WSJ_URL_RE.match(link).groups()
    logger.info("scraping html of {0} {1} {2}".format(symbol, timeframe, report_type))

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
        symbol: e.g. "C6L.SI"
        timeframe: "annual" or "quarter"
        report_type: any string in FINANCIAL_REPORT_TYPES
    """
    logger.info("getting {0} {1} data of {2}".format(timeframe, report_type, symbol))

    url = _get_report_url(symbol, timeframe, report_type)
    html = strict_get(url)

    try:
        raw_data = _scrape_html(html)
    except (IndexError, AttributeError, KeyError) as e:
        msg = "failed to scrape raw data out from the html content of {0} {1} {2}".format(symbol, timeframe, report_type)
        logger.exception(e)
        logger.error(msg)
        raise ScrapingError(msg) from e

    try:    # exception can only be triggered in transpose_items because preprocess returns a generator
        items = preprocess(raw_data, symbol, timeframe, report_type)
        return transpose_items(items)
    except (AssertionError, ValueError) as e:
        msg = "failed to preprocess the raw data of {0} {1} {2}".format(symbol, timeframe, report_type)
        logger.exception(e)
        logger.error(msg)
        raise PreprocessingError(msg) from e
