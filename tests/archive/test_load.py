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
            [[1323000.0,10.18],
             [804000.0,10.17],
             [425000.0,10.14]],
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
              [881000.0,3.26],
              [566000.0,3.28],
              [362000.0,3.30]],
             [[1323000.0,10.18],
              [804000.0,10.17],
              [425000.0,10.14],
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

    def test_parse_top_remark(self):
        self.assertEqual(
            load.parse_top_remark("Fiscal year is April-March. All values sgd Thousands."),
            (3, "SGD", 1000)
        )
        self.assertEqual(
            load.parse_top_remark("Fiscal year is April-March. All values SGD Millions."),
            (3, "SGD", 1000000)
        )
        self.assertEqual(
            load.parse_top_remark("Fiscal year is April-March. All values SGD Billions."),
            (3, "SGD", 1000000000)
        )
        self.assertRaises(
            ValueError,
            load.parse_top_remark,
            "abcdef"
        )

    def test_parse_value(self):
        parsed = load.parse_value("3,456", value_unit=10)

        self.assertTrue(np.isnan(load.parse_value('-', 10)))
        self.assertEqual(load.parse_value("25%", 10), 0.25)
        self.assertEqual(parsed, 34560)
        self.assertIsInstance(parsed, np.int64)
        self.assertEqual(load.parse_value("(3,456)", 10), -34560)
        self.assertEqual(load.parse_value("3,456.78", 10), 34567.8)
        self.assertEqual(load.parse_value("(3,456.78)", 10), -34567.8)

    def test_deduplicate_column_name(self):
        data = (
            ("Sales", [1]),
            ("Cost", [2]),
            ("Cost", [3]),
            ("Tax", [4]),
            ("Cost", [5]),
            ("Tax", [6]),
        )

        self.assertEqual(list(load.deduplicate_column_name(data, extract_columns=None)), [
            ("Sales", [1]),
            ("Cost", [2]),
            ("Cost_2", [3]),
            ("Tax", [4]),
            ("Cost_3", [5]),
            ("Tax_2", [6]),
        ])
        self.assertEqual(list(load.deduplicate_column_name(data, {"Sales"})), [
            ("Sales", [1]),
        ])

    def test_preprocess(self):
        value_data = [
            ["Cash & Short Term Investments", ["4,504", "5,400", "5,488"]],
            ["Liabilities & Shareholders' Equity", ["25,169", "22,589", "22,501"]],
        ]
        obj = {
          "data": [["periods", ["2009", "2010", "2011"]]] + value_data,
          "symbol": "C6L",
          "timeframe": "annual",
          "top_remark": "top_remark",
          "report_type": "balance-sheet",
        }
        extract_columns = {"column1", "column2"}

        with patch("fa.archive.load.UNO_VALUE_UNIT_COLUMNS", {"Cash & Short Term Investments"}), \
             patch("fa.archive.load.parse_top_remark", MagicMock(return_value=(3, "SGD", 1000000))) \
                as mock_parse_top_remark, \
             patch("fa.archive.load.deduplicate_column_name", MagicMock(side_effect=lambda a, b: a)) \
                as mock_deduplicate_column_name, \
             patch("fa.archive.load.parse_value", MagicMock(side_effect=lambda a, b: a)) \
                as mock_parse_value:

            preprocessed = list(load.preprocess(obj, extract_columns))

            mock_parse_top_remark.assert_called_once_with("top_remark")
            mock_deduplicate_column_name.assert_called_once_with(value_data, extract_columns)
            # "Cash & Short Term Investments" is in UNO_VALUE_UNIT_COLUMNS
            mock_parse_value.assert_any_call("4,504", 1)
            mock_parse_value.assert_any_call("22,501", 1000000)

        self.assertEqual(preprocessed, [
            # 04 because of mock_parse_top_remark's return value
            ("Date", [np.datetime64(s) for s in ("2009-04-01", "2010-04-01", "2011-04-01")]),
            ("Cash & Short Term Investments", ["4,504", "5,400", "5,488"]),
            ("Liabilities & Shareholders' Equity", ["25,169", "22,589", "22,501"])
        ])

    def test_load_financial_data(self):
        with patch("fa.archive.load.preprocess", MagicMock(return_value=(("Date", [2, 1, 0]), ("Cash", [4, 5, 6])))) \
            as mock_preprocess:

            df = load.load_financial_data(self.archive_directory, "balance-sheet", "C6L")
            mock_preprocess.assert_called_with({"symbol": "C6L"}, None)    # obj from the fixture json file

            df = load.load_financial_data(self.archive_directory, "balance-sheet", "C6L", ["column1", "column2"])
            mock_preprocess.assert_called_with({"symbol": "C6L"}, {"column1", "column2"})

        expected = pd.DataFrame({"Cash": [6, 5, 4]})    # sorted by Date
        expected.index.name = "Date"
        self.assertFrameEqual(df, expected)

    def test_load_financial_data_all(self):
        columns = ["column1", "column2"]

        with patch("fa.archive.load.FINANCIAL_REPORT_TYPES", ("bs", "cf", "is")), \
             patch("fa.archive.load.load_financial_data", MagicMock(side_effect=lambda a,b,c,d: b)) \
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
