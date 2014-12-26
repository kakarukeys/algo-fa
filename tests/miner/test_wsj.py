import unittest
from unittest.mock import patch, MagicMock
import os.path

from fa.miner import wsj
from fa.miner.exceptions import SymbolError, ScrapingError, PreprocessingError


class TestWSJ(unittest.TestCase):
    def test_get_report_url(self):
        url = wsj._get_report_url("C6L.SI", "annual", "balance-sheet")
        self.assertEqual(url, "http://quotes.wsj.com/SG/XSES/C6L/financials/annual/balance-sheet")

    def test_get_report_url_nasdaq(self):
        url = wsj._get_report_url("MSFT", "quarter", "cash-flow")
        self.assertEqual(url, "http://quotes.wsj.com/MSFT/financials/quarter/cash-flow")

    def test_get_report_url_suffix_not_found(self):
        self.assertRaises(SymbolError, wsj._get_report_url, "MSFT.ABCXYZ", "annual", "balance-sheet")

    def test_scrape_html(self):
        fixture_data_filename = os.path.join(os.path.dirname(__file__), "fixture_data", "C6L.SI_annual_balance-sheet.html")
        with open(fixture_data_filename) as f:
            html = f.read()

        result = wsj._scrape_html(html)

        self.assertEqual(result["symbol_prefix"], "C6L")
        self.assertEqual(result["timeframe"], "annual")
        self.assertEqual(result["report_type"], "balance-sheet")
        self.assertEqual(result["top_remark"], "Fiscal year is April-March. All values SGD Millions.")
        self.assertEqual(result["data"][0], ("periods", ["2010", "2011", "2012", "2013", "2014"]))
        self.assertEqual(result["data"][1], ("Cash & Short Term Investments", ["4,612", "7,832", "5,400", "5,488", "5,305"]))
        self.assertEqual(len(result["data"]), 99)

    def test_get_financial_data(self):
        with patch("fa.miner.wsj._get_report_url", MagicMock(return_value="http://foo")) as mock_get_report_url, \
             patch("fa.miner.wsj.strict_get", MagicMock(return_value="html")) as mock_strict_get, \
             patch("fa.miner.wsj._scrape_html", MagicMock(return_value="raw_data")) as mock_scrape_html, \
             patch("fa.miner.wsj.preprocess", MagicMock(return_value="items")) as mock_preprocess, \
             patch("fa.miner.wsj.transpose_items", MagicMock(return_value="csv rows")) as mock_transpose_items:

            result = wsj.get_financial_data("C6L.SI", "annual", "balance-sheet")

            mock_get_report_url.assert_called_once_with("C6L.SI", "annual", "balance-sheet")
            mock_strict_get.assert_called_once_with("http://foo")
            mock_scrape_html.assert_called_once_with("html")
            mock_preprocess.assert_called_once_with("raw_data", "C6L.SI", "annual", "balance-sheet")
            mock_transpose_items.assert_called_once_with("items")

        self.assertEqual(result, "csv rows")

    def test_get_financial_data_ScrapingError_handling(self):
        with patch("fa.miner.wsj._get_report_url", MagicMock(return_value="http://foo")), \
             patch("fa.miner.wsj.strict_get", MagicMock(return_value="html")):

            for ExceptionClass in (IndexError, AttributeError, KeyError):
                with patch("fa.miner.wsj._scrape_html", MagicMock(side_effect=ExceptionClass)):
                    self.assertRaises(ScrapingError, wsj.get_financial_data, "C6L.SI", "annual", "balance-sheet")

    def test_get_financial_data_PreprocessingError_handling(self):
        with patch("fa.miner.wsj._get_report_url", MagicMock(return_value="http://foo")), \
             patch("fa.miner.wsj.strict_get", MagicMock(return_value="html")), \
             patch("fa.miner.wsj._scrape_html", MagicMock(return_value="raw_data")), \
             patch("fa.miner.wsj.preprocess", MagicMock(return_value="items")):

            for ExceptionClass in (AssertionError, ValueError):
                with patch("fa.miner.wsj.transpose_items", MagicMock(side_effect=ExceptionClass)):
                    self.assertRaises(PreprocessingError, wsj.get_financial_data, "C6L.SI", "annual", "balance-sheet")

if __name__ == "__main__":
    unittest.main()
