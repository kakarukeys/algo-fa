import unittest
from unittest.mock import patch, MagicMock

import numpy as np

from fa.miner import preprocess


class TestPreprocess(unittest.TestCase):
    def test_parse_top_remark(self):
        self.assertEqual(
            preprocess._parse_top_remark("Fiscal year is April-March. All values sgd Thousands."),
            (3, "SGD", 1000)
        )
        self.assertEqual(
            preprocess._parse_top_remark("Fiscal year is April-March. All values SGD Millions."),
            (3, "SGD", 1000000)
        )
        self.assertEqual(
            preprocess._parse_top_remark("Fiscal year is April-March. All values SGD Billions."),
            (3, "SGD", 1000000000)
        )
        self.assertRaises(
            ValueError,
            preprocess._parse_top_remark,
            "abcdef"
        )

    def test_deduplicate_column_name(self):
        data = (
            ("Sales", [1]),
            ("Cost", [2]),
            ("Cost", [3]),
            ("Tax", [4]),
            ("Cost", [5]),
            ("Tax", [6]),
        )

        self.assertEqual(list(preprocess._deduplicate_column_name(data)), [
            ("Sales", [1]),
            ("Cost", [2]),
            ("Cost_2", [3]),
            ("Tax", [4]),
            ("Cost_3", [5]),
            ("Tax_2", [6]),
        ])

    def test_parse_value(self):
        parsed = preprocess._parse_value("3,456", value_unit=10)

        self.assertTrue(np.isnan(preprocess._parse_value('-', 10)))
        self.assertEqual(preprocess._parse_value("25%", 10), 0.25)
        self.assertEqual(parsed, 34560)
        self.assertIsInstance(parsed, np.int64)
        self.assertEqual(preprocess._parse_value("(3,456)", 10), -34560)
        self.assertEqual(preprocess._parse_value("3,456.78", 10), 34567.8)
        self.assertEqual(preprocess._parse_value("(3,456.78)", 10), -34567.8)

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

        with patch("fa.miner.preprocess.UNO_VALUE_UNIT_COLUMNS", {"Cash & Short Term Investments"}), \
             patch("fa.miner.preprocess._parse_top_remark", MagicMock(return_value=(3, "SGD", 1000000))) \
                as mock_parse_top_remark, \
             patch("fa.miner.preprocess._deduplicate_column_name", MagicMock(side_effect=lambda a: a)) \
                as mock_deduplicate_column_name, \
             patch("fa.miner.preprocess._parse_value", MagicMock(side_effect=lambda a, b: a)) \
                as mock_parse_value:

            preprocessed = list(preprocess.preprocess(obj))

            mock_parse_top_remark.assert_called_once_with("top_remark")
            mock_deduplicate_column_name.assert_called_once_with(value_data)
            # "Cash & Short Term Investments" is in UNO_VALUE_UNIT_COLUMNS
            mock_parse_value.assert_any_call("4,504", 1)
            mock_parse_value.assert_any_call("22,501", 1000000)

        self.assertEqual(preprocessed, [
            # 04 because of mock_parse_top_remark's return value
            ("Date", [np.datetime64(s) for s in ("2009-04-01", "2010-04-01", "2011-04-01")]),
            ("Cash & Short Term Investments", ["4,504", "5,400", "5,488"]),
            ("Liabilities & Shareholders' Equity", ["25,169", "22,589", "22,501"])
        ])

if __name__ == "__main__":
    unittest.main()
