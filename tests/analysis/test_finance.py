import unittest
from unittest.mock import patch, MagicMock

from fa.analysis.finance import Metric
from fa.archive.load import FINANCIAL_REPORT_TYPES


class TestMetric(unittest.TestCase):
    def test_from_archive(self):
        with patch("fa.analysis.finance.load_historical_data", MagicMock(return_value='h')) as mock_load_historical_data, \
             patch("fa.analysis.finance.load_financial_data_all", MagicMock(return_value={rt: rt[0] for rt in FINANCIAL_REPORT_TYPES})) as mock_load_financial_data_all, \
             patch("fa.analysis.finance.Metric.__init__", MagicMock(return_value=None)) as mock_constructor:

            obj = Metric.from_archive("/path/to/archive" ,"C6L", 1, b=2)
            mock_load_historical_data.assert_called_once_with("/path/to/archive", "C6L")
            mock_load_financial_data_all.assert_called_once_with("/path/to/archive", "C6L")
            mock_constructor.assert_called_once_with(1, b=2, historical='h', balance_sheet='b', cash_flow='c', income_statement='i')

        self.assertIsInstance(obj, Metric)

if __name__ == "__main__":
    unittest.main()
