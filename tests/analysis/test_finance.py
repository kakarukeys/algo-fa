import unittest
from unittest.mock import patch, MagicMock

import pandas as pd
import numpy as np

from fa.analysis.finance import Metric, DatedMetric
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

    def test_at(self):
        # make up some fake data for testing attribute transfer
        data = lambda: {'d': np.random.randn(3)}
        index = pd.date_range("2012-01-01", periods=3)
        metric = Metric(
            historical=pd.DataFrame(data(), index=index),
            balance_sheet=pd.DataFrame(data(), index=index),
            income_statement=pd.DataFrame(data(), index=index),
            cash_flow=pd.DataFrame(data(), index=index)
        )

        date = pd.Timestamp("2012-12-21")
        obj = metric.at(date)

        self.assertEqual(obj.date, date)
        other_attributes = {k: v for k, v in vars(obj).items() if k != "date"}
        self.assertEqual(other_attributes, vars(metric))
        self.assertIsInstance(obj, DatedMetric)

    def test_calc_return(self):
        data = {"Adj Close": [3.0, 3.5, 4.2], "Close": [3.0, 5.0, 4.2]}
        index = pd.date_range("2012-01-01", periods=3, freq='2D')
        metric = Metric(historical=pd.DataFrame(data, index=index))

        self.assertAlmostEqual(metric.calc_return(pd.Timestamp("2012-01-02"), pd.Timestamp("2012-01-04")), 0.2)
        self.assertAlmostEqual(metric.calc_return(pd.Timestamp("2012-01-02"), pd.Timestamp("2012-01-04"), "Close"), -0.16)

    def test_calc_annual_return(self):
        data = {"Adj Close": [3.0, 3.5, 4.2], "Close": [3.0, 5.0, 4.2]}
        index = pd.date_range("2012-01-01", periods=3, freq='2D')
        metric = Metric(historical=pd.DataFrame(data, index=index))

        self.assertAlmostEqual(metric.calc_annual_return(pd.Timestamp("2012-01-02"), pd.Timestamp("2012-01-04")), 36.5)
        self.assertAlmostEqual(metric.calc_annual_return(pd.Timestamp("2012-01-02"), pd.Timestamp("2012-01-04"), "Close"), -29.2)

if __name__ == "__main__":
    unittest.main()
