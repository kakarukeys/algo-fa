import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

import pandas as pd

from fa.analysis import io
from tests.util import PandasTestCase


class TestIO(PandasTestCase):
    def test_load_fundamental_data(self):
        mock_get_numerical_column_names = MagicMock(return_value=("Volume", "Adj Close"))
        mock_get_fundamentals = MagicMock(return_value=[
            (datetime(2012, 12, 20), 6860, 100.4),
            (datetime(2012, 12, 21), 7850, 99.9),
            (datetime(2012, 12, 22), 3870, 32.6),
        ])

        with patch("fa.analysis.io.get_numerical_column_names", mock_get_numerical_column_names), \
             patch("fa.analysis.io.get_fundamentals", mock_get_fundamentals):
            df = io.load_fundamental_data("price", "C6L.SI")

            mock_get_numerical_column_names.assert_called_once_with("price")
            mock_get_fundamentals.assert_called_once_with("price", "C6L.SI", ["date", "volume", "adj_close"])

        expected = pd.DataFrame(
            [[6860, 100.4],
             [7850, 99.9],
             [3870, 32.6]],
            index=pd.to_datetime(["2012-12-20", "2012-12-21", "2012-12-22"]),
            columns=["Volume", "Adj Close"]
        )
        expected.index.name = "Date"
        self.assertFrameEqual(df, expected)

    def test_load_fundamental_data_select_columns(self):
        mock_get_numerical_column_names = MagicMock(return_value=("Open", "High", "Low", "Close", "Volume", "Adj Close"))
        mock_get_fundamentals = MagicMock(return_value=[
            (datetime(2012, 12, 20), 6860, 100.4),
            (datetime(2012, 12, 21), 7850, 99.9),
            (datetime(2012, 12, 22), 3870, 32.6),
        ])

        with patch("fa.analysis.io.get_numerical_column_names", mock_get_numerical_column_names), \
             patch("fa.analysis.io.get_fundamentals", mock_get_fundamentals):
            df = io.load_fundamental_data("price", "C6L.SI", ["Volume", "Adj Close"])

        expected = pd.DataFrame(
            [[6860, 100.4],
             [7850, 99.9],
             [3870, 32.6]],
            index=pd.to_datetime(["2012-12-20", "2012-12-21", "2012-12-22"]),
            columns=["Volume", "Adj Close"]
        )
        expected.index.name = "Date"
        self.assertFrameEqual(df, expected)

if __name__ == "__main__":
    unittest.main()
