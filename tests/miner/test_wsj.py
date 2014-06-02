import unittest
from unittest.mock import patch, MagicMock

import os.path

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

    def test_scrape_html(self):
        fixture_data_filename = os.path.join(os.path.dirname(__file__), "fixture_data", "C6L_annual_balance-sheet.html")
        with open(fixture_data_filename) as f:
            html = f.read()

        result = wsj._scrape_html(html)

        self.assertEqual(result["symbol"], "C6L")
        self.assertEqual(result["timeframe"], "annual")
        self.assertEqual(result["report_type"], "balance-sheet")
        self.assertEqual(result["top_remark"], "Fiscal year is April-March. All values SGD Millions.")
        self.assertEqual(result["data"][0], ("periods", ["2009", "2010", "2011", "2012", "2013"]))
        self.assertEqual(result["data"][1], ("Cash & Short Term Investments", ["4,504", "4,612", "7,832", "5,400", "5,488"]))
        self.assertEqual(len(result["data"]), 98)

    def test_get_financial_data(self):
        with patch("fa.miner.wsj.get_report_html", MagicMock(return_value="html")) as mock_get_report_html, \
             patch("fa.miner.wsj._scrape_html", MagicMock(return_value="raw_data")) as mock_scrape_html, \
             patch("fa.miner.wsj.preprocess", MagicMock(return_value="items")) as mock_preprocess, \
             patch("fa.miner.wsj.transpose_items", MagicMock(return_value="csv rows")) as mock_transpose_items:

            result = wsj.get_financial_data("C6L", "annual", "balance-sheet")

            mock_get_report_html.assert_called_once_with("C6L", "annual", "balance-sheet")
            mock_scrape_html.assert_called_once_with("html")
            mock_preprocess.assert_called_once_with("raw_data")
            mock_transpose_items.assert_called_once_with("items")

        self.assertEqual(result, "csv rows")

if __name__ == "__main__":
    unittest.main()
