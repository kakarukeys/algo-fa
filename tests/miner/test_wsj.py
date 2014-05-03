import unittest
from unittest.mock import patch, MagicMock

import os.path
from itertools import count

from bs4 import BeautifulSoup

from fa.miner import wsj


class TestWSJ(unittest.TestCase):
    def test_get_report_html(self):
        class MockResponse(object):
            """ HTTP response from opening report page """
            text = "report text"

        with patch("fa.miner.wsj.requests.get", MagicMock(return_value=MockResponse())) as mock_get:
            html = wsj.get_report_html("C6L", "annual", "balance-sheet")
            mock_get.assert_called_once_with("http://quotes.wsj.com/SG/C6L/financials/annual/balance-sheet")

        self.assertEqual(html, "report text")

    def test_get_financial_data(self):
        fixture_data_filename = os.path.join(os.path.dirname(__file__), "fixture_data", "C6L_annual_balance-sheet.html")
        with open(fixture_data_filename) as f:
            html = f.read()

        with patch("fa.miner.wsj.get_report_html", MagicMock(return_value=html)) as mock_get_report_html:
            result = wsj.get_financial_data("C6L", "annual", "balance-sheet")
            mock_get_report_html.assert_called_once_with("C6L", "annual", "balance-sheet")

        self.assertEqual(result["symbol"], "C6L")
        self.assertEqual(result["timeframe"], "annual")
        self.assertEqual(result["report_type"], "balance-sheet")
        self.assertEqual(result["top_remark"], "Fiscal year is April-March. All values SGD Millions.")
        self.assertEqual(result["data"][0], ("periods", ["2009", "2010", "2011", "2012", "2013"]))
        self.assertEqual(result["data"][1], ("Cash & Short Term Investments", ["4,504", "4,612", "7,832", "5,400", "5,488"]))
        self.assertEqual(len(result["data"]), 98)

if __name__ == "__main__":
    unittest.main()
