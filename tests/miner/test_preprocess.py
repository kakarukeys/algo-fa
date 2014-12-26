import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

from fa.miner import preprocess
from fa.miner.exceptions import PreprocessingError


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
            PreprocessingError,
            preprocess._parse_top_remark,
            "abcdef"
        )

    def test_validate(self):
        obj = {
            "data": [
                ["periods", ["2009", "2010", "2011"]],
                ["Cash & Short Term Investments", ["4,504", "5,400", "5,488"]],
            ],
            "symbol_prefix": "C6L",
            "timeframe": "annual",
            "report_type": "balance-sheet",
        }

        try:
            preprocess._validate(obj, "SGD", symbol="C6L.SI", timeframe="annual", report_type="balance-sheet")
        except AssertionError:
            self.fail("obj should be valid.")

        # symbol, timeframe, report_type
        self.assertRaises(AssertionError, preprocess._validate, obj, "SGD", symbol="J7X.SI", timeframe="annual", report_type="balance-sheet")
        self.assertRaises(AssertionError, preprocess._validate, obj, "SGD", symbol="C6L.SI", timeframe="quarter", report_type="balance-sheet")
        self.assertRaises(AssertionError, preprocess._validate, obj, "SGD", symbol="C6L.SI", timeframe="annual", report_type="cash-flow")

        # currency
        self.assertRaises(AssertionError, preprocess._validate, obj, "USD", symbol="C6L.SI", timeframe="annual", report_type="balance-sheet")

    def test_validate_default_currency(self):
        obj = {
            "data": [
                ["periods", ["2009", "2010", "2011"]],
                ["Cash & Short Term Investments", ["4,504", "5,400", "5,488"]],
            ],
            "symbol_prefix": "MSOFT",
            "timeframe": "annual",
            "report_type": "balance-sheet",
        }
        self.assertRaises(AssertionError, preprocess._validate, obj, "SGD", symbol="MSOFT", timeframe="annual", report_type="balance-sheet")

    def test_validate_first_column_name(self):
        obj = {
            "data": [
                ["time", ["2009", "2010", "2011"]],
                ["Cash & Short Term Investments", ["4,504", "5,400", "5,488"]],
            ],
            "symbol_prefix": "C6L",
            "timeframe": "annual",
            "report_type": "balance-sheet",
        }

        self.assertRaises(AssertionError, preprocess._validate, obj, "SGD", symbol="C6L.SI", timeframe="annual", report_type="balance-sheet")

    def test_validate_column_length(self):
        obj = {
            "data": [
                ["periods", ["2009", "2010", "2011"]],
                ["Cash & Short Term Investments", ["4,504", "5,400"]],
            ],
            "symbol_prefix": "C6L",
            "timeframe": "annual",
            "report_type": "balance-sheet",
        }

        self.assertRaises(AssertionError, preprocess._validate, obj, "SGD", symbol="C6L.SI", timeframe="annual", report_type="balance-sheet")

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

        self.assertIs(preprocess._parse_value('-', 10), None)
        self.assertEqual(preprocess._parse_value("25%", 10), 0.25)
        self.assertEqual(parsed, 34560)
        self.assertEqual(preprocess._parse_value("(3,456)", 10), -34560)
        self.assertEqual(preprocess._parse_value("3,456.78", 10), 34567.8)
        self.assertEqual(preprocess._parse_value("(3,456.78)", 10), -34567.8)

    def test_preprocess(self):
        obj = {
            "data": [
                ["periods", ["2009", "2010", "2011"]],
                ["Cash & Short Term Investments", ["4,504", "5,400", "5,488"]],
                ["Cash & Short Term Investments", ["3,504", "4,400", "4,488"]],
                ["Liabilities & Shareholders' Equity", ["25,169", "22,589", "22,501"]],
            ],
            "symbol_prefix": "C6L",
            "timeframe": "annual",
            "top_remark": "Fiscal year is April-March. All values SGD Thousands.",
            "report_type": "balance-sheet",
        }

        with patch("fa.miner.preprocess.UNO_VALUE_UNIT_COLUMNS", {"Cash & Short Term Investments"}):
            preprocessed = list(preprocess.preprocess(obj, "C6L.SI", "annual", "balance-sheet"))

        # first "Cash & Short Term Investments" is in UNO_VALUE_UNIT_COLUMNS
        self.assertEqual(preprocessed, [
            ("Date", [datetime(2009, 4, 1), datetime(2010, 4, 1), datetime(2011, 4, 1)]),
            ("Cash & Short Term Investments", [4504, 5400, 5488]),
            ("Cash & Short Term Investments_2", [3504000, 4400000, 4488000]),
            ("Liabilities & Shareholders' Equity", [25169000, 22589000, 22501000])
        ])

if __name__ == "__main__":
    unittest.main()
