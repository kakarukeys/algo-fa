import unittest
from unittest.mock import patch, MagicMock, call
import os.path

import pandas as pd
import numpy as np

from fa.archive import load
from tests.util import PandasTestCase


class TestLoad(PandasTestCase):
    def setUp(self):
        self.archive_directory = os.path.join(os.path.dirname(__file__), "fixture_data", "test_archive")

    def test_load_historical_data(self):
        with patch("fa.archive.load.HISTORICAL_DATA_COLUMNS", {"Volume": np.float64, "Adj Close": np.float64}):
            df = load.load_historical_data(self.archive_directory, "C6L")

        expected = pd.DataFrame(
            [[1323000.0, 10.18],
             [804000.0, 10.17],
             [425000.0, 10.14]],
            index=pd.to_datetime(["2014-02-20", "2014-02-21", "2014-02-24"]),
            columns=["Volume", "Adj Close"]
        )
        expected.index.name = "Date"
        self.assertFrameEqual(df, expected)

    def test_load_historcal_data__select_columns(self):
        with patch("fa.archive.load.HISTORICAL_DATA_COLUMNS", {"Volume": np.float64, "Adj Close": np.float64}):
            df = load.load_historical_data(self.archive_directory, "C6L", ("Volume",))

        expected = pd.DataFrame(
            [[1323000.0],
             [804000.0],
             [425000.0]],
            index=pd.to_datetime(["2014-02-20", "2014-02-21", "2014-02-24"]),
            columns=["Volume"]
        )
        expected.index.name = "Date"
        self.assertFrameEqual(df, expected)

    def test_load_historical_data_multiple(self):
        with patch("fa.archive.load.HISTORICAL_DATA_COLUMNS", {"Volume": np.float64, "Adj Close": np.float64}):
            p = load.load_historical_data_multiple(self.archive_directory, ("C6L", "B2F"))

        expected = pd.Panel(
            [[[np.nan, np.nan],
              [881000.0, 3.26],
              [566000.0, 3.28],
              [362000.0, 3.30]],
             [[1323000.0, 10.18],
              [804000.0, 10.17],
              [425000.0, 10.14],
              [np.nan, np.nan]]],
            items=["B2F", "C6L"],
            major_axis=pd.to_datetime(["2014-02-20", "2014-02-21", "2014-02-24", "2014-02-25"]),
            minor_axis=["Volume", "Adj Close"]
        )
        self.assertFrameEqual(p, expected)

    def test_load_historical_data_multiple__select_columns(self):
        with patch("fa.archive.load.HISTORICAL_DATA_COLUMNS", {"Volume": np.float64, "Adj Close": np.float64}):
            p = load.load_historical_data_multiple(self.archive_directory, ("C6L", "B2F"), ("Volume",))

        expected = pd.Panel(
            [[[np.nan],
              [881000.0],
              [566000.0],
              [362000.0]],
             [[1323000.0],
              [804000.0],
              [425000.0],
              [np.nan]]],
            items=["B2F", "C6L"],
            major_axis=pd.to_datetime(["2014-02-20", "2014-02-21", "2014-02-24", "2014-02-25"]),
            minor_axis=["Volume"]
        )
        self.assertFrameEqual(p, expected)

    def test_load_financial_data(self):
        df = load.load_financial_data(self.archive_directory, "balance-sheet", "C6L")

        expected = pd.DataFrame(
            [[24610000000, 0.3913],
             [24226000000, 0.4111],
             [np.nan, 0.4038]],
            index=pd.to_datetime(["2010-04-01", "2011-04-01", "2012-04-01"]),
            columns=["Property, Plant & Equipment - Gross", "Total Liabilities / Total Assets"]
        )
        expected.index.name = "Date"
        self.assertFrameEqual(df, expected)

    def test_load_financial_data__select_columns(self):
        df = load.load_financial_data(self.archive_directory, "balance-sheet", "C6L", ["Total Liabilities / Total Assets"])

        expected = pd.DataFrame(
            [[0.3913],
             [0.4111],
             [0.4038]],
            index=pd.to_datetime(["2010-04-01", "2011-04-01", "2012-04-01"]),
            columns=["Total Liabilities / Total Assets"]
        )
        expected.index.name = "Date"
        self.assertFrameEqual(df, expected)

    def test_load_financial_data_all(self):
        columns = ["column1", "column2"]

        with patch("fa.archive.load.FINANCIAL_REPORT_TYPES", ("bs", "cf", "is")), \
             patch("fa.archive.load.load_financial_data", MagicMock(side_effect=lambda a, b, c, d: b)) \
                as mock_load_financial_data:

            data = load.load_financial_data_all(self.archive_directory, "C6L", columns)
            mock_load_financial_data.assert_has_calls([
                call(self.archive_directory, "bs", "C6L", columns),
                call(self.archive_directory, "cf", "C6L", columns),
                call(self.archive_directory, "is", "C6L", columns),
            ], any_order=True)

        self.assertEqual(data, {"bs": "bs", "cf": "cf", "is": "is"})

if __name__ == "__main__":
    unittest.main()
