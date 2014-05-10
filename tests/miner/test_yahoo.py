import unittest
from unittest.mock import patch, MagicMock, call

from datetime import datetime

from fa.miner import yahoo


class TestYahoo(unittest.TestCase):
    def test_get_historical_data(self):
        class MockResponse(object):
            def __init__(self, url):
                """ HTTP response from accessing the API URL """
                symbol = url[36:39]
                self.status_code = 400 if symbol == "err" else 200  # 3rd symbol to trigger error
                self.text = symbol + ".csv"

        with patch("fa.miner.wsj.requests.get", MagicMock(side_effect=MockResponse)) as mock_get:
            result = yahoo.get_historical_data(("C6L", "ZZZ", "err"), datetime(2004, 3, 1), datetime(2014, 3, 1))

            mock_get.assert_has_calls([
                call("http://ichart.yahoo.com/table.csv?s=C6L.SI&a=2&b=1&c=2004&d=2&e=1&f=2014&g=d&ignore=.csv"),
                call("http://ichart.yahoo.com/table.csv?s=ZZZ.SI&a=2&b=1&c=2004&d=2&e=1&f=2014&g=d&ignore=.csv"),
                call("http://ichart.yahoo.com/table.csv?s=err.SI&a=2&b=1&c=2004&d=2&e=1&f=2014&g=d&ignore=.csv"),
            ])

        self.assertEqual(result, {"C6L": "C6L.csv", "ZZZ": "ZZZ.csv", "err": ''})

    def test_constuct_yql(self):
        yql = yahoo._construct_yql(("C6L", "ZZZ"), "yahoo.finance.balancesheet", "annual")
        self.assertEqual(yql, "SELECT * FROM yahoo.finance.balancesheet WHERE symbol IN ('C6L.SI','ZZZ.SI') AND timeframe='annual'")

        yql = yahoo._construct_yql(("C6L", "ZZZ"), "yahoo.finance.keystats", None)
        self.assertEqual(yql, "SELECT * FROM yahoo.finance.keystats WHERE symbol IN ('C6L.SI','ZZZ.SI')")

    def test_get_financial_data(self):
        class MockResponse(object):
            """ HTTP response from accessing the API URL """
            def json(self):
                return {
                  "query": {
                    "count": 2,
                    "created": "2014-05-02T14:09:49Z",
                    "lang": "en-US",
                    "results": {
                      "balancesheet": [
                        {"symbol": "C6L.SI"},
                        {"symbol": "ZZZ.SI"}
                      ]
                    }
                  }
                }

        with patch("fa.miner.yahoo._construct_yql", MagicMock(return_value="yql")) as mock_construct_yql, \
             patch("fa.miner.yahoo.requests.get", MagicMock(return_value=MockResponse())) as mock_get:

            result = yahoo.get_financial_data(("C6L", "ZZZ"), "annual", "balancesheet")

            mock_construct_yql.assert_called_once_with(("C6L", "ZZZ"), "yahoo.finance.balancesheet", "annual")
            mock_get.assert_called_once_with(yahoo.YQL_API_URL, params={
                "q": "yql",
                "format": "json",
                "env": "store://datatables.org/alltableswithkeys",
            })

        self.assertEqual(result, {"C6L": {"symbol": "C6L.SI"}, "ZZZ": {"symbol": "ZZZ.SI"}})

    def test_get_financial_data__single_symbol(self):
        class MockResponse(object):
            """ HTTP response from accessing the API URL """
            def json(self):
                return {
                  "query": {
                    "count": 1,
                    "created": "2014-05-02T14:29:42Z",
                    "lang": "en-US",
                    "results": {
                      "balancesheet": {"symbol": "C6L.SI"}
                    }
                  }
                }

        with patch("fa.miner.yahoo._construct_yql", MagicMock(return_value="yql")) as mock_construct_yql, \
             patch("fa.miner.yahoo.requests.get", MagicMock(return_value=MockResponse())) as mock_get:

            result = yahoo.get_financial_data(("C6L",), "annual", "balancesheet")

        self.assertEqual(result, {"C6L": {"symbol": "C6L.SI"}})

    def test_get_financial_data__keystats(self):
        class MockResponse(object):
            """ HTTP response from accessing the API URL """
            def json(self):
                return {
                  "query": {
                    "count": 2,
                    "created": "2014-05-02T14:16:42Z",
                    "lang": "en-US",
                    "results": {
                      "stats": [
                        {"symbol": "C6L.SI"},
                        {"symbol": "ZZZ.SI"}
                      ]
                    }
                  }
                }

        with patch("fa.miner.yahoo._construct_yql", MagicMock(return_value="yql")) as mock_construct_yql, \
             patch("fa.miner.yahoo.requests.get", MagicMock(return_value=MockResponse())) as mock_get:

            result = yahoo.get_financial_data(("C6L", "ZZZ"), "quarterly", "keystats")
            mock_construct_yql.assert_called_once_with(("C6L", "ZZZ"), "yahoo.finance.keystats", None)

        self.assertEqual(result, {"C6L": {"symbol": "C6L.SI"}, "ZZZ": {"symbol": "ZZZ.SI"}})

if __name__ == "__main__":
    unittest.main()